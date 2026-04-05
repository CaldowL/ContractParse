import os
from concurrent.futures import ThreadPoolExecutor

from ContarctParser.config import CHAT_MAX_EPOCH
from ContarctParser.utils.tools import read_file
from ContarctParser.utils.mcpm import McpManager
from ContarctParser.utils.request_ai import request_chat
from ContarctParser.utils.log import logger


class ContractParser:
    def __init__(self):
        self.mcp = McpManager()

    def parse_signal_contract(self, contract: str):
        if os.path.isfile(contract):
            contract = read_file(contract)

        txt = read_file("prompts/main.txt")
        system_, user_ = txt.split("##")[:2]
        user_ = user_.replace("{{content}}", contract)
        messages_local = [
            {
                "role": "system",
                "content": system_
            },
            {
                "role": "user",
                "content": user_
            }
        ]

        idx_epoch = 0
        while True:
            idx_epoch += 1
            if idx_epoch >= CHAT_MAX_EPOCH:
                logger.error("迭代次数内未能解决问题")
                return None

            res = request_chat(messages_local, functions=self.mcp.get_mcp_json())
            choice = res.choices[0]
            messages_local.append(choice.message.model_dump())
            if choice.finish_reason == "tool_calls":
                tool_call = choice.message.tool_calls[0]
                if tool_call.function.name == self.mcp.final_tool:
                    return self.mcp.handle_mcp_request(tool_call)

                result_call = self.mcp.handle_mcp_request(tool_call)
                messages_local.append({"role": "tool", "tool_call_id": tool_call.id, "content": result_call})

    def parse_contract(self, contracts: str | list):
        """
        批量执行解析任务
        :param contracts:
        :return:
        """
        if isinstance(contracts, str):
            contracts = [contracts]

        with ThreadPoolExecutor(max_workers=len(contracts)) as executor:
            futures = [executor.submit(self.parse_signal_contract, contract) for contract in contracts]
            results = [future.result() for future in futures]
        return results


if __name__ == '__main__':
    contractParser = ContractParser()
    s = """
文件名：CU12-3456-7890-123456.doc
合同内容：
《场地管理服务协议》
协议编号：CU12-3456-7890-123456
甲方：中国移动通信集团江苏有限公司南京分公司
乙方：南京浦口科创物业管理有限公司

为支持甲方在南京地区数字移动通信系统工程建设的需要，乙方愿意将管理权的房屋及场地提供给甲方管理。场地位于：南京市浦口区江浦街道中圣北街20号。场地管理使用面积为：30平方米。约定年管理服务费25000元（含税，按年支付，币种人民币）。期限自2014年9月5日至2024年9月4日。协议到期后，若双方无异议，本协议自动续期一年。
    """
    logger.info(contractParser.parse_signal_contract(s))

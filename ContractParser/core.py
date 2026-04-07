import os
import json
from concurrent.futures import ThreadPoolExecutor

from ContractParser.config import CHAT_MAX_EPOCH, DIR_LIB_ROOT
from ContractParser.utils.tools import read_file, filter_dumps
from ContractParser.utils.mcpm import McpManager
from ContractParser.utils.request_ai import request_chat
from ContractParser.utils.log import logger


class ContractParser:
    def __init__(self):
        self.mcp = McpManager()

    def _parse_signal_contract(self, contract: str):
        if os.path.isfile(contract):
            contract = read_file(contract)

        # 读系统提示词
        txt = read_file(os.path.join(DIR_LIB_ROOT, "prompts/main.txt"))
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

            # 添加到历史记录
            messages_local.append(filter_dumps(choice.message.model_dump()))
            if choice.finish_reason == "tool_calls":
                tool_call = choice.message.tool_calls[0]
                result_call = self.mcp.handle_mcp_request(tool_call)

                logger.debug(result_call)
                # 最终的结果，无需后续处理
                if tool_call.function.name == self.mcp.final_tool:
                    try:
                        if isinstance(result_call, str):
                            raise Exception("生成结果错误！函数参数错误！")
                        json.dumps(result_call)
                    except Exception as e:
                        logger.debug(f"解析出现问题，继续执行 {e}")
                        messages_local.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(e)})
                        continue

                    # 文件名兜底策略
                    if not result_call.get("合同编号") and os.path.isfile(contract):
                        result_call["合同编号"] = os.path.basename(contract)
                    return result_call

                messages_local.append({"role": "tool", "tool_call_id": tool_call.id, "content": result_call})

            # 模型认为可以结束，但是正常流程下仅存在调用final_tool的mcp即可，不存在此分支
            if choice.finish_reason == "stop":
                logger.error("当前数据不满足识别条件")
                return None

    def parse_signal_contract(self, contract: str):
        try:
            return self._parse_signal_contract(contract)
        except Exception as e:
            logger.error(e)
            return None

    def parse_contract(self, contracts: str | list):
        """
        批量执行解析任务
        :param contracts:
        :return:
        """
        if isinstance(contracts, str):
            contracts = [contracts]

        # 线程池，数量不多可以加按照合同数量来
        with ThreadPoolExecutor(max_workers=len(contracts)) as executor:
            futures = [executor.submit(self.parse_signal_contract, contract) for contract in contracts]
            results = [future.result() for future in futures]
        return results


if __name__ == '__main__':
    contractParser = ContractParser()
    logger.info(contractParser.parse_signal_contract("../files/2.txt"))

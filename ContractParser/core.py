import os
from concurrent.futures import ThreadPoolExecutor

from ContractParser.config import CHAT_MAX_EPOCH, DIR_LIB_ROOT
from ContractParser.utils.tools import read_file
from ContractParser.utils.mcpm import McpManager
from ContractParser.utils.request_ai import request_chat
from ContractParser.utils.log import logger


class ContractParser:
    def __init__(self):
        self.mcp = McpManager()

    def parse_signal_contract(self, contract: str):
        if os.path.isfile(contract):
            contract = read_file(contract)

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
            messages_local.append(choice.message.model_dump())
            if choice.finish_reason == "tool_calls":
                tool_call = choice.message.tool_calls[0]
                if tool_call.function.name == self.mcp.final_tool:
                    return self.mcp.handle_mcp_request(tool_call)

                result_call = self.mcp.handle_mcp_request(tool_call)
                messages_local.append({"role": "tool", "tool_call_id": tool_call.id, "content": result_call})

            if choice.finish_reason == "stop":
                logger.error("当前数据不满足识别条件")
                return None

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
    logger.info(contractParser.parse_signal_contract("../files/1.txt"))

import traceback

import requests

from openai.types.chat import ChatCompletionMessageFunctionToolCall

from ContarctParser.utils.log import logger
from ContarctParser.config import *


class McpManager:
    def __init__(self):
        pass

    @staticmethod
    def summary_info(
            number: str,
            type_: str,
            address: str,
            price: str,
            pos: list[str],
            area: str,
            period: list[str],
            ps: str
    ):
        """
        总结信息，后续无需传入大模型
        :param number: 合同编号，字符串格式。
        :param type_: 合同类型
        :param address: 场地地址
        :param price: 金额
        :param pos: 位置，列表，[经度,纬度]
        :param area: 场地面积
        :param period: 租期，起止日期格式,[开始时间,结束时间]
        :param ps: 备注
        :return:
        """
        res = {
            "合同编号": number,
            "合同类型": type_,
            "地址": address,
            "金额": price,
            "经纬度": f"{pos[0]},{pos[1]}",
            "面积": area,
            "租期": f"{period[0]}-{period[1]}",
            "备注": ps
        }
        return res

    @staticmethod
    def get_addr_pos(keyword: str) -> str:
        """
        根据地点查询经纬度。返回经纬度的列表 [经度,纬度]
        :param keyword:地点
        :return: list
        """
        params = {
            "key": API_AMAP_KEY,
            "keywords": keyword
        }
        resp = requests.get(url=API_AMAP_BASEURL, params=params).json()
        if int(resp.get("count", 0)) < 1:
            return "未找到当前地址，请忽略此字段"
        return resp["pois"][0]["location"]

    @staticmethod
    def get_mcp_json():
        summary_info_tool = {
            "type": "function",
            "function": {
                "name": "summary_info",
                "description": "总结合同信息，根据用户提示填充参数，若未识别出真是结果，则传入对应数据类型的默认空值",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "number": {
                            "type": "string",
                            "description": "合同编号"
                        },
                        "type_": {
                            "type": "string",
                            "description": "合同类型"
                        },
                        "address": {
                            "type": "string",
                            "description": "场地地址"
                        },
                        "price": {
                            "type": "string",
                            "description": "金额"
                        },
                        "pos": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "位置，[经度, 纬度]"
                        },
                        "area": {
                            "type": "string",
                            "description": "场地面积"
                        },
                        "period": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "租期，[开始时间, 结束时间]"
                        },
                        "ps": {
                            "type": "string",
                            "description": "备注"
                        }
                    },
                    "required": [
                        "number",
                        "type_",
                        "address",
                        "price",
                        "pos",
                        "area",
                        "period",
                        "ps"
                    ]
                }
            }
        }
        get_addr_pos_tool = {
            "type": "function",
            "function": {
                "name": "get_addr_pos",
                "description": "根据地点查询经纬度，返回经纬度的列表 [经度, 纬度]",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "地点关键词"
                        }
                    },
                    "required": [
                        "keyword"
                    ]
                }
            }
        }

        return [summary_info_tool, get_addr_pos_tool]

    @property
    def final_tool(self):
        return "summary_info"

    def handle_mcp_request(self, tool_call: ChatCompletionMessageFunctionToolCall):
        try:
            arguments = eval(tool_call.function.arguments)
            if tool_call.function.name == "summary_info":
                return self.summary_info(**arguments)
            if tool_call.function.name == "get_addr_pos":
                return self.get_addr_pos(**arguments)
        except Exception as e:
            logger.debug(traceback.format_exc())

        return "未找到匹配的方法"


if __name__ == '__main__':
    print(McpManager.get_addr_pos("安徽大渡口镇滨江时代广场"))

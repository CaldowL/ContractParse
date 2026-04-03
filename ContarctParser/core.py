import pdb
import os

from ContarctParser.utils.tools import read_file

from ContarctParser.utils.request_ai import request_chat


class ContractParser:
    def __init__(self):
        pass

    def parse_contract(self, contract: str):
        if os.path.isfile(contract):
            txt = read_file(contract)
        else:
            txt = contract

        txt = read_file("prompts/main.txt").replace("{{content}}", txt)
        system_, user_ = txt.split("##")
        res = request_chat([
            {
                "role": "system",
                "content": system_
            },
            {
                "role": "user",
                "content": user_
            }
        ])
        pdb.set_trace()
        # res.choices[0].message.content
        res.choices[0].finish_reason


if __name__ == '__main__':
    contractParser = ContractParser()
    s = """
文件名：CU12-3456-7890-123456.doc
合同内容：
《场地管理服务协议》
协议编号：CU12-3456-7890-123456
甲方：中国移动通信集团江苏有限公司南京分公司
乙方：南京浦口科创物业管理有限公司

为支持甲方在南京地区数字移动通信系统工程建设的需要，乙方愿意将管理权的房屋及场地提供给甲方管理。场地位于：南京市浦口区江浦街道中圣北街20号（经纬度：118.61696, 32.06180）。场地管理使用面积为：30平方米。约定年管理服务费25000元（含税，按年支付，币种人民币）。期限自2014年9月5日至2024年9月4日。协议到期后，若双方无异议，本协议自动续期一年。
    """
    contractParser.parse_contract(s)

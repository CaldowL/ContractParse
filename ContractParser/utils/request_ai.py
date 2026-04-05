from retrying import retry
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from ContractParser.config import *
from ContractParser.utils.log import logger

client = OpenAI(base_url=MODEL_BASE_URL, api_key=MODEL_API_KEY)


@retry(stop_max_attempt_number=3)
def request_chat(message: list | str, functions: list = None) -> ChatCompletion:
    logger.debug(message)

    if functions is None:
        functions = []
    if isinstance(message, str):
        message = [{"role": "user", "content": message}]

    resp = client.chat.completions.create(model=MODEL_NAME, messages=message, tools=functions)
    return resp


if __name__ == '__main__':
    logger.info(request_chat("你好"))

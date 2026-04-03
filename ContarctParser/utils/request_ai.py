from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from ContarctParser.config import *
from ContarctParser.utils.log import logger

client = OpenAI(base_url=MODEL_BASE_URL, api_key=MODEL_API_KEY)


def request_chat(message: list | str) -> ChatCompletion:
    logger.debug(message)
    if isinstance(message, str):
        message = [{"role": "user", "content": message}]

    resp = client.chat.completions.create(model=MODEL_NAME, messages=message)
    return resp


if __name__ == '__main__':
    print(request_chat("你好"))

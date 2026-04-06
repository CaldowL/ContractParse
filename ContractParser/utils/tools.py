def read_file(file_path: str) -> str:
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    raise Exception("暂不支持的文件格式")


def filter_dumps(body: dict) -> dict:
    pass

import logging
import sys


class ColoredFormatter(logging.Formatter):
    # ANSI 颜色码
    COLORS = {
        logging.DEBUG: "\033[36m",  # 青色
        logging.INFO: "\033[32m",  # 绿色
        logging.WARNING: "\033[33m",  # 黄色
        logging.ERROR: "\033[31m",  # 红色
        logging.CRITICAL: "\033[1;35m",  # 紫色加粗
    }
    RESET = "\033[0m"  # 重置颜色

    def format(self, record):
        # 给日志消息添加颜色
        color = self.COLORS.get(record.levelno, self.RESET)
        record.levelname = f"{color}{record.levelname:<8}{self.RESET}"
        # 给整个消息加上颜色
        record.msg = f"{color}{record.getMessage()}{self.RESET}"
        return super().format(record)


def create_logger(name: str = "app", level: int = logging.DEBUG) -> logging.Logger:
    """
    创建一个全局logger
    :param name:
    :param level:
    :return:
    """
    logger_ = logging.getLogger(name)
    logger_.setLevel(level)

    # 多次import避免重复创建
    if logger_.handlers:
        return logger_

    fmt = "%(asctime)s | %(levelname)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # 直接输出控制台
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter(fmt, datefmt=datefmt))
    logger_.addHandler(console_handler)

    return logger_


logger = create_logger("app", level=logging.DEBUG)

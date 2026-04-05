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
        # 给整个消息加上颜色（可选，取决于你想要的效果）
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
    # 避免重复添加 handler（模块多次调用时）
    if logger_.handlers:
        return logger_

    # ---------- 日志格式 ----------
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # ---------- 控制台 Handler（带颜色） ----------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter(fmt, datefmt=datefmt))
    logger_.addHandler(console_handler)

    return logger_


logger = create_logger("app", level=logging.DEBUG)

if __name__ == "__main__":
    logger.debug("这是一条 DEBUG 消息 — 用于调试")
    logger.info("这是一条 INFO 消息 — 程序正常运行")
    logger.warning("这是一条 WARNING 消息 — 存在潜在问题")
    logger.error("这是一条 ERROR 消息 — 发生错误")
    logger.critical("这是一条 CRITICAL 消息 — 严重错误，程序可能崩溃")

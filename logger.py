# =========================
# logger.py
# 项目的日志配置
# =========================


# 【新增1】
import logging

# 【新增2】
import os


# =========================
# 1. 创建日志目录
# =========================


# 【新增3】
LOG_DIR = "logs"


# 【新增4】
os.makedirs(
    LOG_DIR,
    exist_ok=True
)


# 【新增5】
LOG_FILE = os.path.join(
    LOG_DIR,
    "agent.log"
)


# =========================
# 2. 创建 Logger
# =========================


# 【新增6】
logger = logging.getLogger(
    "mini_agent"
)


# 【新增7】
logger.setLevel(
    logging.INFO
)


# =========================
# 3. 日志格式
# =========================


# 【新增8】
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


# =========================
# 4. 控制台日志
# =========================


# 【新增9】
console_handler = logging.StreamHandler()


# 【新增10】
console_handler.setFormatter(
    formatter
)


# =========================
# 5. 文件日志
# =========================


# 【新增11】
file_handler = logging.FileHandler(
    LOG_FILE,
    encoding="utf-8"
)


# 【新增12】
file_handler.setFormatter(
    formatter
)


# =========================
# 6. 把 Handler 加到 Logger
# =========================


# 【新增13】
if not logger.handlers:

    logger.addHandler(
        console_handler
    )

    logger.addHandler(
        file_handler
    )
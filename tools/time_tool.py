# =========================
# time_tool.py
# 时间工具
# =========================


# 【移动2】
from datetime import datetime


# 【移动3】
def get_current_time():

    current_time = datetime.now()

    return current_time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
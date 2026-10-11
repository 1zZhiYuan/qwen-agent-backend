# =========================
# config.py
# 项目的统一配置
# =========================


# 【新增1】
# 主 Agent 使用的模型
MAIN_AGENT_MODEL = "qwen3.8-27b"


# 【新增2】
# Web Search Tool 使用的联网模型
SEARCH_MODEL = "qwen-plus"


# 【新增3】
# Agent 最多允许执行多少轮
MAX_AGENT_STEPS = 10


# 【新增4】
# 短期记忆最多保留多少轮用户对话
MAX_USER_TURNS = 3
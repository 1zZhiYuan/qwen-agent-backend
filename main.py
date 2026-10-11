import os

import dashscope
from dotenv import load_dotenv


# 【新增4】
# 从 agent.py 中导入 run_agent
from agent import run_agent
# 【新增6】
from prompts import create_initial_messages

# =========================
# 1. 基础配置
# =========================

load_dotenv()

api_key = os.getenv("DASHSCOPE_API_KEY")

if not api_key:
    raise ValueError(
        "没有读取到 DASHSCOPE_API_KEY，请检查 .env 文件"
    )

dashscope.api_key = api_key


# =========================
# 2. 启动程序
# =========================

print("Mini Agent 已启动")
print("输入 exit 可以退出程序")


# 【修改7】
messages = create_initial_messages()


while True:

    user_input = input("\n你：")


    if user_input == "exit":

        print("Agent：再见！")

        break


    answer = run_agent(
        user_input,
        messages
    )


    print(
        "\nAgent：",
        answer
    )
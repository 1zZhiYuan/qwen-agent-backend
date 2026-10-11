# =========================
# tests/test_core.py
# Mini Agent 核心功能测试
# =========================


# 【新增1】
from tools.calculator import calculator


# 【新增2】
from prompts import create_initial_messages


# 【新增3】
from agent import trim_messages


# =========================
# 1. Calculator 测试
# =========================


# 【新增4】
def test_calculator():

    result = calculator(
        88,
        12
    )


    # 【新增5】
    assert result == 100


# =========================
# 2. Initial Messages 测试
# =========================


# 【新增6】
def test_create_initial_messages():

    messages = (
        create_initial_messages()
    )


    # 【新增7】
    assert len(messages) == 1


    # 【新增8】
    assert (
        messages[0]["role"]
        == "system"
    )


    # 【新增9】
    assert (
        "AI助手"
        in messages[0]["content"][0]["text"]
    )


# =========================
# 3. Memory Trim 测试
# =========================


# 【新增10】
def test_trim_messages():

    messages = [
        {
            "role": "system",
            "content": [
                {
                    "text": "System"
                }
            ]
        },

        {
            "role": "user",
            "content": [
                {
                    "text": "第1轮"
                }
            ]
        },

        {
            "role": "assistant",
            "content": [
                {
                    "text": "回答1"
                }
            ]
        },

        {
            "role": "user",
            "content": [
                {
                    "text": "第2轮"
                }
            ]
        },

        {
            "role": "assistant",
            "content": [
                {
                    "text": "回答2"
                }
            ]
        },

        {
            "role": "user",
            "content": [
                {
                    "text": "第3轮"
                }
            ]
        },

        {
            "role": "assistant",
            "content": [
                {
                    "text": "回答3"
                }
            ]
        },

        {
            "role": "user",
            "content": [
                {
                    "text": "第4轮"
                }
            ]
        },

        {
            "role": "assistant",
            "content": [
                {
                    "text": "回答4"
                }
            ]
        }
    ]


    # 【新增11】
    trim_messages(
        messages,
        max_user_turns=3
    )


    # 【新增12】
    assert (
        messages[0]["role"]
        == "system"
    )


    # 【新增13】
    user_messages = [
        message
        for message in messages
        if message["role"] == "user"
    ]


    # 【新增14】
    assert len(user_messages) == 3


    # 【新增15】
    assert (
        user_messages[0]["content"][0]["text"]
        == "第2轮"
    )


    # 【新增16】
    assert (
        user_messages[-1]["content"][0]["text"]
        == "第4轮"
    )
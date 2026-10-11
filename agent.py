# =========================
# agent.py
# 负责 Agent 的核心运行逻辑
# =========================


import json

from dashscope import MultiModalConversation

from tools import tools, tool_functions

from config import (
    MAIN_AGENT_MODEL,
    MAX_AGENT_STEPS,
    MAX_USER_TURNS
)

from logger import logger


# =========================
# 1. Memory 管理
# =========================


def trim_messages(
    messages,
    max_user_turns=MAX_USER_TURNS
):

    user_indexes = []


    for index, message in enumerate(messages):

        if message.get("role") == "user":

            user_indexes.append(index)


    if len(user_indexes) <= max_user_turns:

        return


    first_keep_index = (
        user_indexes[-max_user_turns]
    )


    system_message = messages[0]


    recent_messages = messages[
        first_keep_index:
    ]


    messages[:] = [
        system_message,
        *recent_messages
    ]


    logger.info(
        "Agent Context 已裁剪，仅保留最近 %s 轮用户对话",
        max_user_turns
    )


# =========================
# 2. Agent 核心函数
# =========================


def run_agent(user_input, messages):

    # 【新增1】
    # messages 保存完整聊天历史
    #
    # working_messages 是本次真正发送给 LLM 的上下文
    #
    # list(messages) 会创建一个新的列表，
    # 因此后面对 working_messages 的裁剪
    # 不会删除完整历史
    working_messages = list(
        messages
    )


    # 【修改2】
    # 现在只裁剪 working_messages
    # 不再裁剪完整 messages
    trim_messages(
        working_messages
    )


    user_message = {
        "role": "user",
        "content": [
            {
                "text": user_input
            }
        ]
    }


    # 【新增3】
    # 给 LLM 使用
    working_messages.append(
        user_message
    )


    # 【新增4】
    # 同时加入完整聊天历史
    messages.append(
        user_message
    )


    logger.info(
        "收到用户问题：%s",
        user_input
    )


    # =========================
    # Agent Loop
    # =========================


    for step in range(
        MAX_AGENT_STEPS
    ):

        logger.info(
            "Agent 第 %s 步",
            step + 1
        )


        # 【修改5】
        # 注意这里不再发送完整 messages
        #
        # 而是发送经过 Sliding Window
        # 裁剪后的 working_messages
        response = MultiModalConversation.call(
            model=MAIN_AGENT_MODEL,

            messages=working_messages,

            tools=tools,

            parallel_tool_calls=True
        )


        # =========================
        # 检查模型 API
        # =========================


        if response.status_code != 200:

            logger.error(
                "模型调用失败 | "
                "status_code=%s | "
                "code=%s | "
                "message=%s",

                response.status_code,
                response.code,
                response.message
            )


            return (
                "模型调用失败，"
                "请检查日志中的错误信息。"
            )


        assistant_message = (
            response
            .output
            .choices[0]
            .message
        )


        # 【新增6】
        # Assistant Message
        # 同时加入：
        #
        # 1. LLM工作上下文
        # 2. 完整聊天历史
        working_messages.append(
            assistant_message
        )


        messages.append(
            assistant_message
        )


        tool_calls = getattr(
            assistant_message,
            "tool_calls",
            None
        )


        # =========================
        # 不需要 Tool
        # =========================


        if not tool_calls:

            final_text = (
                assistant_message
                .content[0]["text"]
            )


            logger.info(
                "Agent 已生成最终回答"
            )


            return final_text


        # =========================
        # 处理 Tool Calls
        # =========================


        for tool_call in tool_calls:

            tool_name = (
                tool_call["function"]["name"]
            )


            arguments_str = (
                tool_call["function"]["arguments"]
            )


            tool_call_id = (
                tool_call["id"]
            )


            logger.info(
                "模型请求调用工具：%s",
                tool_name
            )


            logger.info(
                "工具原始参数：%s",
                arguments_str
            )


            # =========================
            # 解析参数
            # =========================


            try:

                arguments = json.loads(
                    arguments_str
                )


            except json.JSONDecodeError as e:

                result = (
                    "工具调用失败："
                    "模型生成的参数不是合法 JSON。"
                    f"错误信息：{str(e)}"
                )


                logger.error(
                    "工具 %s 参数 JSON 解析失败：%s",
                    tool_name,
                    e
                )


                tool_message = {
                    "role": "tool",
                    "content": result,
                    "tool_call_id": tool_call_id
                }


                # 【修改7】
                # Tool Result 也要同时进入两份列表
                working_messages.append(
                    tool_message
                )


                messages.append(
                    tool_message
                )


                continue


            logger.info(
                "工具解析后的参数：%s",
                arguments
            )


            # =========================
            # 查找 Tool
            # =========================


            tool_function = (
                tool_functions.get(
                    tool_name
                )
            )


            if tool_function is None:

                result = (
                    "工具调用失败："
                    f"没有找到名为 {tool_name} 的工具"
                )


                logger.warning(
                    "未找到工具：%s",
                    tool_name
                )


            else:

                try:

                    logger.info(
                        "开始执行工具：%s",
                        tool_name
                    )


                    result = tool_function(
                        **arguments
                    )


                    logger.info(
                        "工具执行完成：%s",
                        tool_name
                    )


                except TypeError as e:

                    result = (
                        "工具调用失败："
                        "工具参数不正确。"
                        f"错误信息：{str(e)}"
                    )


                    logger.error(
                        "工具 %s 参数错误：%s",
                        tool_name,
                        e
                    )


                except Exception:

                    result = (
                        "工具调用失败："
                        "工具执行过程中发生异常。"
                    )


                    logger.exception(
                        "工具 %s 执行异常",
                        tool_name
                    )


            logger.info(
                "工具 %s 返回结果：%s",
                tool_name,
                result
            )


            tool_message = {
                "role": "tool",
                "content": str(result),
                "tool_call_id": tool_call_id
            }


            # 【修改8】
            # Tool结果：
            # 一份给当前LLM继续思考
            working_messages.append(
                tool_message
            )


            # 【新增9】
            # 一份进入完整历史
            messages.append(
                tool_message
            )


    logger.warning(
        "Agent 达到最大执行次数：%s",
        MAX_AGENT_STEPS
    )


    return (
        "Agent 执行次数过多，已停止。"
    )
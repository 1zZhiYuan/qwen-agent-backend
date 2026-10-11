# =========================
# api.py
# Mini Agent 的 FastAPI 接口
# =========================


# 【新增1】
import threading


from fastapi import FastAPI
from fastapi import HTTPException

from pydantic import BaseModel

from agent import run_agent

from logger import logger

from prompts import create_initial_messages

from session_store import (
    load_session,
    save_session,
    delete_session_from_db,
    list_sessions,
    get_session_messages
)


# =========================
# 1. 创建 FastAPI 应用
# =========================


app = FastAPI(
    title="Mini Agent API",
    description="一个自己实现的 Tool Calling Agent",
    version="1.0.0"
)


# =========================
# 2. 请求数据结构
# =========================


class ChatRequest(BaseModel):

    session_id: str

    message: str


# =========================
# 3. Session Lock 管理
# =========================


# 【新增2】
# key：
# session_id
#
# value：
# 这个 Session 自己的 Lock
session_locks = {}


# 【新增3】
# 专门保护 session_locks 这个字典本身
session_locks_guard = threading.Lock()


# 【新增4】
def get_session_lock(
    session_id
):

    # 【新增5】
    # 先保护 session_locks 字典，
    # 避免两个线程同时给同一个 session 创建 Lock
    with session_locks_guard:

        # 【新增6】
        if session_id not in session_locks:

            # 【新增7】
            session_locks[session_id] = (
                threading.Lock()
            )


        # 【新增8】
        return session_locks[
            session_id
        ]


# =========================
# 4. 健康检查
# =========================


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# =========================
# 5. Agent聊天接口
# =========================


@app.post("/chat")
def chat(
    request: ChatRequest
):

    session_id = request.session_id

    user_input = request.message


    # 【新增9】
    # 找到当前 Session 自己的 Lock
    session_lock = get_session_lock(
        session_id
    )


    # 【新增10】
    # 同一个 Session 同一时间只能有一个请求进入
    with session_lock:

        logger.info(
            "会话 %s 获取 Lock",
            session_id
        )


        messages = load_session(
            session_id
        )


        if messages is None:

            messages = (
                create_initial_messages()
            )


            logger.info(
                "创建新会话：%s",
                session_id
            )


        answer = run_agent(
            user_input,
            messages
        )


        save_session(
            session_id,
            messages
        )


        logger.info(
            "会话 %s 已保存到 SQLite",
            session_id
        )


        # 【新增11】
        logger.info(
            "会话 %s 即将释放 Lock",
            session_id
        )


        return {
            "session_id": session_id,
            "answer": answer
        }


# =========================
# 6. 查询所有 Session
# =========================


@app.get("/sessions")
def get_sessions():

    session_list = (
        list_sessions()
    )


    return {
        "count": len(
            session_list
        ),

        "sessions": session_list
    }


# =========================
# 7. 查看 Session
# =========================


@app.get(
    "/sessions/{session_id}"
)
def get_session(
    session_id: str
):

    messages = load_session(
        session_id
    )


    if messages is None:

        raise HTTPException(
            status_code=404,
            detail="Session 不存在"
        )


    return {
        "session_id": session_id,

        "exists": True,

        "message_count": len(
            messages
        )
    }


# =========================
# 8. 查看 Session 聊天历史
# =========================


@app.get(
    "/sessions/{session_id}/messages"
)
def get_messages(
    session_id: str
):

    messages = (
        get_session_messages(
            session_id
        )
    )


    if messages is None:

        raise HTTPException(
            status_code=404,
            detail="Session 不存在"
        )


    return {
        "session_id": session_id,

        "message_count": len(
            messages
        ),

        "messages": messages
    }


# =========================
# 9. 删除 Session
# =========================


@app.delete(
    "/sessions/{session_id}"
)
def delete_session(
    session_id: str
):

    # 【新增12】
    # 删除时也必须拿同一个 Session Lock
    session_lock = get_session_lock(
        session_id
    )


    # 【新增13】
    with session_lock:

        deleted = (
            delete_session_from_db(
                session_id
            )
        )


        if not deleted:

            raise HTTPException(
                status_code=404,
                detail="Session 不存在"
            )


        logger.info(
            "从 SQLite 删除会话：%s",
            session_id
        )


        return {
            "session_id": session_id,
            "deleted": True
        }
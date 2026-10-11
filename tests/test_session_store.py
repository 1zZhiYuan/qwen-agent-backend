# =========================
# tests/test_session_store.py
# SQLite Session Store 自动化测试
# =========================


# 【新增1】
import json


# 【新增2】
import session_store


# 【新增3】
from prompts import create_initial_messages


# =========================
# 1. 创建测试数据库
# =========================


# 【新增4】
def prepare_test_database(
    tmp_path,
    monkeypatch
):

    # 【新增5】
    test_db_path = (
        tmp_path
        / "test_sessions.db"
    )


    # 【新增6】
    monkeypatch.setattr(
        session_store,
        "DB_PATH",
        str(test_db_path)
    )


    # 【新增7】
    session_store.init_db()


    return test_db_path


# =========================
# 2. Session 保存和读取
# =========================


# 【新增8】
def test_save_and_load_session(
    tmp_path,
    monkeypatch
):

    prepare_test_database(
        tmp_path,
        monkeypatch
    )


    session_id = "test_save_load"


    # 【新增9】
    messages = (
        create_initial_messages()
    )


    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "text": "你好"
                }
            ]
        }
    )


    messages.append(
        {
            "role": "assistant",
            "content": [
                {
                    "text": "你好，有什么可以帮你？"
                }
            ]
        }
    )


    # 【新增10】
    session_store.save_session(
        session_id,
        messages
    )


    # 【新增11】
    loaded_messages = (
        session_store.load_session(
            session_id
        )
    )


    # 【新增12】
    assert loaded_messages is not None


    # 【新增13】
    assert len(loaded_messages) == 3


    # 【新增14】
    assert (
        loaded_messages[1]["role"]
        == "user"
    )


    # 【新增15】
    assert (
        loaded_messages[1]
        ["content"][0]["text"]
        == "你好"
    )


# =========================
# 3. 增量保存测试
# =========================


# 【新增16】
def test_incremental_save(
    tmp_path,
    monkeypatch
):

    prepare_test_database(
        tmp_path,
        monkeypatch
    )


    session_id = (
        "test_incremental"
    )


    # =========================
    # 第一次保存
    # =========================


    messages = (
        create_initial_messages()
    )


    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "text": "第一轮"
                }
            ]
        }
    )


    messages.append(
        {
            "role": "assistant",
            "content": [
                {
                    "text": "回答第一轮"
                }
            ]
        }
    )


    session_store.save_session(
        session_id,
        messages
    )


    # 【新增17】
    first_history = (
        session_store
        .get_session_messages(
            session_id
        )
    )


    # 【新增18】
    first_ids = [
        message["id"]
        for message in first_history
    ]


    # =========================
    # 第二次保存
    # =========================


    # 【新增19】
    loaded_messages = (
        session_store.load_session(
            session_id
        )
    )


    loaded_messages.append(
        {
            "role": "user",
            "content": [
                {
                    "text": "第二轮"
                }
            ]
        }
    )


    loaded_messages.append(
        {
            "role": "assistant",
            "content": [
                {
                    "text": "回答第二轮"
                }
            ]
        }
    )


    # 【新增20】
    session_store.save_session(
        session_id,
        loaded_messages
    )


    # 【新增21】
    second_history = (
        session_store
        .get_session_messages(
            session_id
        )
    )


    # 【新增22】
    second_ids = [
        message["id"]
        for message in second_history
    ]


    # 【新增23】
    assert len(first_history) == 3


    # 【新增24】
    assert len(second_history) == 5


    # 【新增25】
    assert (
        second_ids[:3]
        == first_ids
    )


    # 【新增26】
    assert (
        second_history[-2]
        ["message"]
        ["content"][0]["text"]
        == "第二轮"
    )


# =========================
# 4. 级联删除测试
# =========================


# 【新增27】
def test_delete_session_cascade(
    tmp_path,
    monkeypatch
):

    prepare_test_database(
        tmp_path,
        monkeypatch
    )


    session_id = (
        "test_delete"
    )


    messages = (
        create_initial_messages()
    )


    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "text": "准备删除"
                }
            ]
        }
    )


    session_store.save_session(
        session_id,
        messages
    )


    # 【新增28】
    deleted = (
        session_store
        .delete_session_from_db(
            session_id
        )
    )


    # 【新增29】
    assert deleted is True


    # 【新增30】
    assert (
        session_store.load_session(
            session_id
        )
        is None
    )


    # =========================
    # 验证 Messages 也被级联删除
    # =========================


    # 【新增31】
    connection = (
        session_store
        .get_connection()
    )


    cursor = connection.cursor()


    # 【新增32】
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM messages
        WHERE session_id = ?
        """,
        (session_id,)
    )


    message_count = (
        cursor.fetchone()[0]
    )


    connection.close()


    # 【新增33】
    assert message_count == 0
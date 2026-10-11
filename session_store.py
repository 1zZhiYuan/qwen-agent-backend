# =========================
# session_store.py
# SQLite Session / Message 持久化
# =========================


import os
import json
import sqlite3


# =========================
# 1. 数据库配置
# =========================


DATA_DIR = "data"


os.makedirs(
    DATA_DIR,
    exist_ok=True
)


DB_PATH = os.path.join(
    DATA_DIR,
    "sessions.db"
)


# =========================
# 2. 获取数据库连接
# =========================


def get_connection():

    connection = sqlite3.connect(
        DB_PATH
    )


    connection.execute(
        "PRAGMA foreign_keys = ON"
    )


    return connection


# =========================
# 3. 初始化数据库
# =========================


def init_db():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (

            session_id TEXT PRIMARY KEY,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT NOT NULL,

            role TEXT NOT NULL,

            message_json TEXT NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (session_id)
                REFERENCES sessions(session_id)
                ON DELETE CASCADE
        )
        """
    )


    connection.commit()

    connection.close()


# =========================
# 4. 读取 Session
# =========================


def load_session(session_id):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT session_id
        FROM sessions
        WHERE session_id = ?
        """,
        (session_id,)
    )


    session_row = cursor.fetchone()


    if session_row is None:

        connection.close()

        return None


    cursor.execute(
        """
        SELECT message_json
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session_id,)
    )


    rows = cursor.fetchall()


    connection.close()


    messages = []


    for row in rows:

        message_json = row[0]


        message = json.loads(
            message_json
        )


        messages.append(
            message
        )


    return messages


# =========================
# 5. 增量保存 Session
# =========================


def save_session(
    session_id,
    messages
):

    connection = get_connection()

    cursor = connection.cursor()


    # =========================
    # 5.1 创建 / 更新 Session
    # =========================


    cursor.execute(
        """
        INSERT INTO sessions (
            session_id
        )
        VALUES (?)

        ON CONFLICT(session_id)
        DO UPDATE SET
            updated_at = CURRENT_TIMESTAMP
        """,
        (session_id,)
    )


    # =========================
    # 5.2 查询数据库已有多少 Message
    # =========================


    # 【修改10】
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM messages
        WHERE session_id = ?
        """,
        (session_id,)
    )


    # 【新增11】
    saved_message_count = (
        cursor.fetchone()[0]
    )


    # =========================
    # 5.3 找出新增 Message
    # =========================


    # 【新增12】
    new_messages = messages[
        saved_message_count:
    ]


    # 【新增13】
    logger_message = (
        f"Session {session_id}: "
        f"数据库已有 {saved_message_count} 条，"
        f"本次新增 {len(new_messages)} 条"
    )


    # 这里暂时用 print 不合适，
    # 所以下面不真正输出 logger_message。
    # 它只是帮助你理解这两个数字。


    # =========================
    # 5.4 只保存新增 Message
    # =========================


    # 【修改14】
    for message in new_messages:

        if isinstance(
            message,
            dict
        ):

            message_dict = message

        else:

            message_dict = dict(
                message
            )


        role = message_dict.get(
            "role",
            "unknown"
        )


        message_json = json.dumps(
            message_dict,
            ensure_ascii=False,
            default=dict
        )


        cursor.execute(
            """
            INSERT INTO messages (
                session_id,
                role,
                message_json
            )
            VALUES (?, ?, ?)
            """,
            (
                session_id,
                role,
                message_json
            )
        )


    # 【修改15】
    # 不再 DELETE 旧消息
    # 只提交新增内容
    connection.commit()

    connection.close()


# =========================
# 6. 删除 Session
# =========================


def delete_session_from_db(
    session_id
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        DELETE FROM sessions
        WHERE session_id = ?
        """,
        (session_id,)
    )


    deleted_count = cursor.rowcount


    connection.commit()

    connection.close()


    return deleted_count > 0


# =========================
# 7. 查询所有 Session
# =========================


def list_sessions(
    limit=50
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT
            s.session_id,
            s.created_at,
            s.updated_at,
            COUNT(m.id) AS message_count

        FROM sessions AS s

        LEFT JOIN messages AS m
            ON s.session_id = m.session_id

        GROUP BY
            s.session_id,
            s.created_at,
            s.updated_at

        ORDER BY
            s.updated_at DESC

        LIMIT ?
        """,
        (limit,)
    )


    rows = cursor.fetchall()


    result = []


    for row in rows:

        session_id = row[0]

        created_at = row[1]

        updated_at = row[2]

        message_count = row[3]


        result.append(
            {
                "session_id": session_id,
                "created_at": created_at,
                "updated_at": updated_at,
                "message_count": message_count
            }
        )


    connection.close()


    return result


# =========================
# 8. 查询 Session 聊天记录
# =========================


def get_session_messages(
    session_id
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT session_id
        FROM sessions
        WHERE session_id = ?
        """,
        (session_id,)
    )


    session_row = cursor.fetchone()


    if session_row is None:

        connection.close()

        return None


    cursor.execute(
        """
        SELECT
            id,
            role,
            message_json,
            created_at
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session_id,)
    )


    rows = cursor.fetchall()


    result = []


    for row in rows:

        message_id = row[0]

        role = row[1]

        message_json = row[2]

        created_at = row[3]


        message_data = json.loads(
            message_json
        )


        result.append(
            {
                "id": message_id,
                "role": role,
                "message": message_data,
                "created_at": created_at
            }
        )


    connection.close()


    return result


# =========================
# 9. 初始化数据库
# =========================


init_db()
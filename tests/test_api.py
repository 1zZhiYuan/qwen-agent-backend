# =========================
# tests/test_api.py
# FastAPI 接口自动化测试
# =========================


# 【新增1】
from fastapi.testclient import TestClient


# 【新增2】
import api


# =========================
# 1. 创建测试客户端
# =========================


# 【新增3】
client = TestClient(
    api.app
)


# =========================
# 2. Health API
# =========================


# 【新增4】
def test_health():

    # 【新增5】
    response = client.get(
        "/health"
    )


    # 【新增6】
    assert response.status_code == 200


    # 【新增7】
    assert response.json() == {
        "status": "ok"
    }


# =========================
# 3. 不存在的 Session
# =========================


# 【新增8】
def test_session_not_found():

    response = client.get(
        "/sessions/"
        "session_that_does_not_exist"
    )


    # 【新增9】
    assert response.status_code == 404


    # 【新增10】
    assert response.json() == {
        "detail": "Session 不存在"
    }


# =========================
# 4. Chat API
# =========================


# 【新增11】
def test_chat(
    monkeypatch
):

    # =========================
    # Fake Agent
    # =========================


    # 【新增12】
    def fake_run_agent(
        user_input,
        messages
    ):

        # 【新增13】
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "text": user_input
                    }
                ]
            }
        )


        messages.append(
            {
                "role": "assistant",
                "content": [
                    {
                        "text": "这是测试回答"
                    }
                ]
            }
        )


        # 【新增14】
        return "这是测试回答"


    # =========================
    # 替换真实 Agent
    # =========================


    # 【新增15】
    monkeypatch.setattr(
        api,
        "run_agent",
        fake_run_agent
    )


    # =========================
    # 清理测试 Session
    # =========================


    # 【新增16】
    session_id = (
        "pytest_chat_test"
    )


    api.delete_session_from_db(
        session_id
    )


    # =========================
    # 发 POST 请求
    # =========================


    # 【新增17】
    response = client.post(
        "/chat",

        json={
            "session_id": session_id,
            "message": "你好"
        }
    )


    # =========================
    # 验证 Response
    # =========================


    # 【新增18】
    assert response.status_code == 200


    # 【新增19】
    data = response.json()


    assert (
        data["session_id"]
        == session_id
    )


    assert (
        data["answer"]
        == "这是测试回答"
    )


    # =========================
    # 清理数据库
    # =========================


    # 【新增20】
    api.delete_session_from_db(
        session_id
    )
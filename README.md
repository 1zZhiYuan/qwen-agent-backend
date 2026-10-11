
# MiniAgent — 基于 Qwen 的工具调用 AI Agent

从零实现的轻量级 AI Agent 后端项目。

项目使用阿里云百炼 Qwen 模型，通过 Tool Calling 实现工具调用，支持多轮对话、会话管理、SQLite 持久化及 Docker 容器化。

## 1. 项目功能

- 基于 Qwen 的 Agent Loop
- Tool Calling 与工具注册机制
- 支持计算器、时间、天气、联网搜索工具
- 支持多工具调用及异常处理
- Sliding Window 短期记忆
- 多 Session 会话隔离
- SQLite 聊天历史持久化
- 增量保存消息
- 基于 Lock 的单进程会话并发保护
- FastAPI REST API
- 日志记录与 pytest 自动化测试
- Docker 部署

## 2. 技术栈

| 类型 | 技术 |
|---|---|
| 开发语言 | Python |
| 大模型 | Qwen / DashScope |
| Web 框架 | FastAPI |
| 数据验证 | Pydantic |
| 数据库 | SQLite |
| HTTP 请求 | requests |
| 自动化测试 | pytest |
| 容器化 | Docker |

## 3. Agent 工作原理

User Request
    ↓
FastAPI
    ↓
Session Management
    ↓
Load Chat History
    ↓
Sliding Window Memory
    ↓
Qwen LLM
    ↓
Tool Calling Decision
    ↓
Tool Registry
    ↓
Tool Execution
    ↓
Tool Result
    ↓
LLM Final Answer
    ↓
Incremental SQLite Persistence

## 4. 项目结构

project1/
├── api.py
├── main.py
├── agent.py
├── config.py
├── logger.py
├── prompts.py
├── session_store.py
├── tools/
├── tests/
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example
├── requirements.txt
└── README.md

## 5. 环境配置

推荐使用 Python 3.14。

在 Windows PowerShell 中进入项目目录：

    cd "F:\AA\1\agent-learning\project1"

创建虚拟环境（首次运行时）：

    python -m venv .venv

激活虚拟环境：

    .\.venv\Scripts\Activate.ps1

安装依赖：

    python -m pip install -r requirements.txt

复制环境变量模板：

    Copy-Item .env.example .env

编辑 `.env`，填入自己的 DashScope API Key。

注意：不要将真实 API Key 上传到 GitHub。

## 6. 本地运行

在项目根目录执行：

    python -m uvicorn api:app --reload

浏览器访问：

http://127.0.0.1:8000/docs

## 7. API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /health | 健康检查 |
| POST | /chat | Agent 聊天 |
| GET | /sessions | 获取会话列表 |
| GET | /sessions/{session_id} | 查询会话 |
| GET | /sessions/{session_id}/messages | 获取聊天历史 |
| DELETE | /sessions/{session_id} | 删除会话 |

### POST /chat 示例

Request:

    {
      "session_id": "demo",
      "message": "88 + 12 等于多少？"
    }

Response:

    {
      "session_id": "demo",
      "answer": "88 + 12 = 100"
    }

实际回答文字可能略有不同。

## 8. Docker 部署

在安装并启动 Docker Desktop 后，于项目根目录执行：

    docker build -t mini-agent:1.0 .

创建持久化目录：

    New-Item -ItemType Directory -Force .\data, .\logs

启动容器（Windows PowerShell）：

    docker run -d --name mini-agent -p 8000:8000 --env-file .env -v "${PWD}/data:/app/data" -v "${PWD}/logs:/app/logs" mini-agent:1.0

查看容器：

    docker ps

查看日志：

    docker logs mini-agent

浏览器访问：

http://127.0.0.1:8000/docs

## 9. 自动化测试

在项目根目录、已激活虚拟环境的 PowerShell 中执行：

    python -m pip install pytest httpx

运行：

    python -m pytest -v

测试涵盖核心函数、Memory、部分 API 行为和 SQLite 持久化逻辑。

## 10. 安全说明

- API Key 通过环境变量配置
- `.env` 不提交到 Git
- Docker 镜像不包含本地 `.env`
- SQLite 数据和日志通过 Bind Mount 持久化

## 11. 项目定位

本项目主要用于学习和展示 AI Agent 的底层工作原理及基础后端工程实现。

当前是单机学习项目，并非完整的生产级分布式 Agent 平台。

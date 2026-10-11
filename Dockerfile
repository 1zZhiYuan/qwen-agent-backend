# =========================
# Dockerfile
# MiniAgent Docker Image
# =========================


# 【修改1】与本地Python及刚下载的镜像版本保持一致
FROM python:3.14-slim


# 2. Container 工作目录
WORKDIR /app


# 3. 先复制依赖文件
COPY requirements.txt .


# 4. 安装依赖
RUN pip install --no-cache-dir -r requirements.txt


# 5. 复制项目代码
COPY . .


# 6. 声明 FastAPI 端口
EXPOSE 8000


# 7. 启动 FastAPI
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
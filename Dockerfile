FROM python:3.10-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY src/ ./src/
COPY pyproject.toml .

# 安装 Python 依赖
RUN pip install --no-cache-dir \
    fastmcp>=0.4.0 \
    httpx>=0.27.0 \
    pydantic>=2.0.0 \
    pydantic-settings>=2.0.0 \
    uvicorn \
    starlette

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/sse')" || exit 1

# 启动命令
CMD ["python", "-m", "src"]

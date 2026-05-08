FROM python:3.10-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 拷贝 whl 包和资源压缩包
COPY cosyvoice-ttsfrd/resource.zip /tmp/resource.zip
COPY cosyvoice-ttsfrd/ttsfrd_dependency-0.1-py3-none-any.whl /tmp/
COPY cosyvoice-ttsfrd/ttsfrd-0.4.2-cp310-cp310-linux_x86_64.whl /tmp/

# 解压资源到 /app/resource
RUN unzip /tmp/resource.zip -d /app && rm /tmp/resource.zip

# 安装依赖
RUN pip install --no-cache-dir \
    /tmp/ttsfrd_dependency-0.1-py3-none-any.whl \
    /tmp/ttsfrd-0.4.2-cp310-cp310-linux_x86_64.whl \
    && rm /tmp/*.whl

# 安装 Python 依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir fastapi "uvicorn[standard]"

# 拷贝应用代码
COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 1: 解压资源（resource.zip 极少变动，独立缓存）
FROM astral/uv:python3.10-trixie AS resource-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY cosyvoice-ttsfrd/resource.zip /tmp/resource.zip
RUN unzip /tmp/resource.zip -d /extracted && rm /tmp/resource.zip

# Stage 2: 安装重量级 whl 依赖（whl 文件变动时重建，与资源互不影响）
FROM astral/uv:python3.10-trixie AS whl-builder

WORKDIR /app

RUN uv venv .venv

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY cosyvoice-ttsfrd/ttsfrd_dependency-0.1-py3-none-any.whl /tmp/
COPY cosyvoice-ttsfrd/ttsfrd-0.4.2-cp310-cp310-linux_x86_64.whl /tmp/
RUN uv pip install --no-cache \
    /tmp/ttsfrd_dependency-0.1-py3-none-any.whl \
    /tmp/ttsfrd-0.4.2-cp310-cp310-linux_x86_64.whl \
    && rm /tmp/*.whl

# Stage 3: 安装应用层依赖（pyproject.toml / uv.lock 变动时重建）
FROM whl-builder AS app-builder

COPY pyproject.toml uv.lock* ./
RUN uv pip install --no-cache fastapi "uvicorn[standard]"

# Stage 4: 最终运行时（仅代码变动时重建此层）
FROM astral/uv:python3.10-trixie AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=resource-builder /extracted/ ./
COPY --from=app-builder /app/.venv .venv

COPY main.py .

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

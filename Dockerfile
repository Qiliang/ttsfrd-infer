FROM astral/uv:python3.10-trixie AS builder

RUN sed -i 's/deb.debian.org/mirrors.huaweicloud.com/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY cosyvoice-ttsfrd/resource.zip /tmp/resource.zip
RUN unzip /tmp/resource.zip -d /extracted && rm /tmp/resource.zip

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY cosyvoice-ttsfrd/ttsfrd_dependency-0.1-py3-none-any.whl /tmp/
COPY cosyvoice-ttsfrd/ttsfrd-0.4.2-cp310-cp310-linux_x86_64.whl /tmp/
RUN uv pip install --no-cache \
    /tmp/ttsfrd_dependency-0.1-py3-none-any.whl \
    /tmp/ttsfrd-0.4.2-cp310-cp310-linux_x86_64.whl \
    && rm /tmp/*.whl



# 最终运行时（仅代码变动时重建此层）
FROM astral/uv:python3.10-trixie AS runtime

WORKDIR /app

RUN sed -i 's/deb.debian.org/mirrors.huaweicloud.com/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /extracted/ ./
COPY --from=builder /app/.venv .venv

COPY *.py .

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# 服务根路径前缀，例如 /ttsfrd/ping；可用 docker run -e CONTEXT_PATH=myapp 覆盖
ENV CONTEXT_PATH=ttsfrd

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY agent/ ./agent/
COPY servers/ ./servers/
COPY mcp-config.json .
COPY .env.example .

CMD ["python", "-c", "from agent.main import run_agent; import asyncio; asyncio.run(run_agent('给我生成一份关于 Pilbara 锂矿的今日简报'))"]

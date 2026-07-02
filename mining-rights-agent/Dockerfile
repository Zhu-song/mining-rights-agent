FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY agent/ ./agent/
COPY servers/ ./servers/
COPY test_mcp.py .

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["python", "-m", "agent.main"]
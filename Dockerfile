# 카카오클라우드(PlayMCP in KC) Git 소스 빌드용 Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# HTTP(Endpoint) 모드로 실행
ENV MCP_HTTP=1
ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080

CMD ["python", "server.py"]

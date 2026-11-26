# Ally API on Render (or any container host): FastAPI under uvicorn on $PORT.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=8002
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["sh", "-c", "python -m uvicorn app:app --host 0.0.0.0 --port ${PORT} --no-access-log"]

# ==============================================================================
# Base Stage: Python 3.11 Slim
# ==============================================================================
FROM python:3.11-slim AS base

# Ngăn Python tạo file .pyc và bật unbuffered log
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Cài đặt system dependencies cần thiết (curl, libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy và cài đặt requirements
COPY backend/app-api/requirements.txt /app/backend/app-api/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/app-api/requirements.txt

# Copy source code
COPY backend /app/backend

WORKDIR /app/backend/app-api

EXPOSE 8000

# Khởi chạy Uvicorn với chế độ reload cho môi trường development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

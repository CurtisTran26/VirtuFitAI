FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app/backend/app-api

COPY backend/shared /app/backend/shared
COPY backend/app-api/requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app-api/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

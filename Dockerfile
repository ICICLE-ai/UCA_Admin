FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY src ./src

RUN useradd -m appuser
USER appuser

ENV PYTHONPATH=/app
EXPOSE 8081

CMD ["uvicorn", "src.database.rules_engine.api:app", "--host", "0.0.0.0", "--port", "8081"]
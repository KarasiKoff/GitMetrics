# syntax=docker/dockerfile:1

# --- Stage 1: builder — установка зависимостей и пакета ---
FROM python:3.12-slim AS builder

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# --- Stage 2: runtime — минимальный образ только для запуска CLI ---
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_DIR=/app/logs

WORKDIR /app

RUN mkdir -p /app/logs

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/gitmetrics /usr/local/bin/gitmetrics

ENTRYPOINT ["gitmetrics"]
CMD ["--help"]

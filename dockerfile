FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src ./src

RUN pip install --upgrade pip \
    && pip install .

ENV PYTHONPATH=/app

# 👇 YA NO hardcodeamos el worker
CMD ["sh", "-c", "python ${WORKER_PATH}"]
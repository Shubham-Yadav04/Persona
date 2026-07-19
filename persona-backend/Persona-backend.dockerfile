FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

ENV HOST=0.0.0.0
ENV PORT=8000

CMD sh -c "uvicorn backend:app --host ${HOST} --port ${PORT}"
FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY infra/docker/worker/worker.py /app/worker.py

CMD ["python", "/app/worker.py"]


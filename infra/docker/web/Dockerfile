FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY infra/docker/common/server.py /app/server.py

EXPOSE 3000
CMD ["python", "/app/server.py"]


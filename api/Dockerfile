# Build from repo root:
#   docker build -f api/Dockerfile -t invoice-sentinel-api .
# Or from api/ after copying seed:
#   docker build -t invoice-sentinel-api .

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    UPLOAD_DIR=/data/uploads \
    PORT=8080

COPY api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY api/ /app/
COPY data/seed-cases.json /data/seed-cases.json

RUN mkdir -p /data/uploads

EXPOSE 8080
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}

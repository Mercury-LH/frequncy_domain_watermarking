FROM node:20-slim AS frontend
WORKDIR /build
COPY webapp/frontend/package.json webapp/frontend/package-lock.json ./
RUN npm ci
COPY webapp/frontend ./
RUN npm run build

FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends fonts-noto-cjk && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY webapp/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY src /app/src
COPY webapp/backend /app/webapp/backend
COPY --from=frontend /build/dist /app/webapp/frontend/dist
ENV PYTHONPATH=/app:/app/src
EXPOSE 7860
CMD ["uvicorn", "webapp.backend.app:app", "--host", "0.0.0.0", "--port", "7860", "--proxy-headers", "--forwarded-allow-ips=*"]

# ==============================================================================
# CUTLINE — Google Cloud Run Multi-Stage Containerfile
# Builds React frontend and serves via FastAPI on Google Cloud Run
# ==============================================================================

# Stage 1: Build React Frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Runtime
FROM python:3.13-slim AS runner

# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install system certificates and security updates
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./backend/

# Copy built frontend assets into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Non-root security user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]

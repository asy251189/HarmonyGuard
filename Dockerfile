FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for better pip performance
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1

# Create a minimal requirements file for core dependencies
COPY requirements-minimal.txt .

# Install core dependencies first
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Create directories for models and lexicons
RUN mkdir -p models lexicons

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "app.py"]

-----------------------------------------------------------------

services:
  abuse-detector:
    build: 
      context: .
      dockerfile: Dockerfile
      args:
        ABUSE_API_VERSION: ${TAG}
    image: ${IMAGE}:${TAG}
    ports:
      - "8000:8000"
    environment:
      - ABUSE_API_DEBUG=false
      - ABUSE_API_REDIS_ENABLED=false
      - ABUSE_API_MODEL_CACHE_DIR=/app/models
      - ABUSE_API_DEVICE=cpu
    volumes:
      - model_cache:/app/models
      - ./lexicons:/app/lexicons
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    profiles:
      - with-redis

volumes:
  redis_data:
  model_cache:
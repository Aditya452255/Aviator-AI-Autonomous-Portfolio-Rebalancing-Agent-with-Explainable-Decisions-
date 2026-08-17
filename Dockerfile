# Multi-Stage Production Dockerfile for Aviator AI
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application source code
COPY . .

# Expose FastAPI Health server port (8000) and Gradio Dashboard port (7860)
EXPOSE 8000 7860

# Default entrypoint executing main pipeline and starting Production Service
CMD ["python", "main.py", "--phase", "9"]

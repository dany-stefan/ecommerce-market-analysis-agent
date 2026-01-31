# Multi-stage Docker build for E-commerce Market Analysis Agent
# Question 1: Containerization for easier deployment and evaluation

# Stage 1: Base Python environment
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM dependencies as application

# Copy application code
COPY ../src /app/src
COPY ../config /app/config
COPY ../tests /app/tests
COPY ../main.py /app/
COPY ../requirements.txt /app/
COPY api.py /app/

# Create directories for outputs
RUN mkdir -p reports logs

# Health check for API mode
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose API port
EXPOSE 8000

# Default command: Run REST API server
CMD ["python", "api.py"]

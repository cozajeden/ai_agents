FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install curl for health checks
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code into a proper Python package path
COPY . /app/app

# Create data directory and set permissions
RUN mkdir -p /app/data \
    && chmod 755 /app/data

# Create non-root user
# RUN adduser --disabled-password --gecos '' appuser \
#     && chown -R appuser:appuser /app
# USER appuser

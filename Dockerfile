# Dockerfile for Oil Spill Portal App
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY OilSpillPortal/requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY OilSpillPortal /app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (7860 is HF default)
EXPOSE 7860

# Run with Gunicorn for Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "portal_app:app"]

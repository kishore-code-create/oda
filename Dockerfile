# Dockerfile for Oil Spill Detection App
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libopencv-dev \
    python3-opencv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ODA\(OIL\)/oil_spill_detection/oil_spill_detection/requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn python-dotenv

# Copy application code
COPY ODA\(OIL\)/oil_spill_detection/oil_spill_detection /app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (7860 is HF default)
EXPOSE 7860

# Run with Gunicorn for Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app1:app"]

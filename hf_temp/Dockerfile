FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ libpq-dev libopencv-dev python3-opencv git curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn python-dotenv
COPY . /app
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 7860
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app1:app"]

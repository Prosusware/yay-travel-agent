FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port for Cloud Run
EXPOSE 8080

# Set environment variables for Uvicorn
ENV PORT=8080

# Start FastAPI app with Uvicorn - use PORT environment variable
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]

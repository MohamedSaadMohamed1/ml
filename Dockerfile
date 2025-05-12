FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies with optimized PyTorch
RUN pip install --no-cache-dir -r requirements.txt

# Clean up to reduce image size
RUN apt-get remove -y gcc python3-dev \
    && apt-get autoremove -y \
    && rm -rf /root/.cache/pip

COPY . .

EXPOSE 8000

# Run with single worker to conserve memory
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
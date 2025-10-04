FROM python:3.11-slim

WORKDIR /app

# Install system dependencies in a single layer and clean up
RUN apt-get update && apt-get install -y \
    libarchive-dev \
    build-essential \
    libtool \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install flask

# Copy application files
COPY app/ /app/

CMD ["python", "app.py"]

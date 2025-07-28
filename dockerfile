# version 2
FROM python:3.11-slim

# Set environment variables...
ENV DEBIAN_FRONTEND=noninteractive
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV PYTHONPATH /app

# Install system-level dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libmagic1 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install Python packages
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy your backend source code
COPY backend/ /app/

# Run the application
CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind "0.0.0.0:$PORT"
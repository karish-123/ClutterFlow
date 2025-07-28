# Start with your chosen Python version
FROM python:3.11-slim

# Set environment variables to non-interactively install packages
ENV DEBIAN_FRONTEND=noninteractive
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# THIS IS THE FIX: Add the app directory to Python's path
ENV PYTHONPATH /app

# Install system-level dependencies required by your Python libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libmagic1 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY backend/requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your backend source code into the container
COPY backend/ /app/

# This "shell form" of CMD ensures that $PORT is correctly interpreted.
CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind "0.0.0.0:$PORT"
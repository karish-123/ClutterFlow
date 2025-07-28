# Start with your chosen Python version
FROM python:3.11-slim

# Set environment variables to non-interactively install packages
ENV DEBIAN_FRONTEND=noninteractive
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Install system-level dependencies required by your Python libraries
# - tesseract-ocr: Required by pytesseract
# - poppler-utils: Required by pdf2image
# - libmagic1: Required by python-magic
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

# Cloud Run provides the PORT environment variable that your container should listen on
# Gunicorn is a production-grade server to run our FastAPI app
CMD ["gunicorn", "-w" , "4" , "-k" , "uvicorn.workers.UvicornWorker" , "main:app" , "--bind" , "0.0.0.0:$PORT"]

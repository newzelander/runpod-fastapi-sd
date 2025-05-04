FROM python:3.10-slim

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpython3.10-dev \
        build-essential \
        git \
        curl \
        libatlas-base-dev \
        libomp-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy handler script
COPY handler.py .

# Set the command to run the handler
CMD ["python", "handler.py"]

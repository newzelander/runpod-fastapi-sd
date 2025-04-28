# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables to avoid Python buffering logs
ENV PYTHONUNBUFFERED 1

# Set working directory in the container
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the preload_model.py script into the container
COPY preload_model.py /app/preload_model.py

# Set the entrypoint to run preload_model.py
ENTRYPOINT ["python", "/app/preload_model.py"]

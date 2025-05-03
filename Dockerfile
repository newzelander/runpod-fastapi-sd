# Use an official Python runtime
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Prevent output buffering
ENV PYTHONUNBUFFERED=1

# Run this on container start (used by RunPod serverless)
ENTRYPOINT ["python", "/app/main.py"]

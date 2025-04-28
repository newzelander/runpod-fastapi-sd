# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables to avoid Python buffering logs
ENV PYTHONUNBUFFERED 1

# Set working directory in the container
WORKDIR /app

# Install necessary system dependencies (if any)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy the Python script into the container
COPY delete_all.py /app/delete_all.py

# Set the entrypoint to run delete_all.py
ENTRYPOINT ["python", "/app/delete_all.py"]

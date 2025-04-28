# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables to avoid Python buffering logs
ENV PYTHONUNBUFFERED 1

# Set working directory in the container
WORKDIR /app

# Install necessary system dependencies (no need for any specific ones for this task)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (in this case, only logging is used which is built-in)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the delete_all.py script into the container
COPY delete_all.py /app/delete_all.py

# Set the entrypoint to run delete_all.py
ENTRYPOINT ["python", "/app/delete_all.py"]

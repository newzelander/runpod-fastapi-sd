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
COPY delete_model.py /app/delete_model.py

# Set the entrypoint to run delete_model.py (which runs once and exits)
ENTRYPOINT ["python", "/app/delete_model.py"]

# Ensure the container stops after the script finishes
CMD ["exit"]

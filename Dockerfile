# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies and Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED 1

# Set the correct entry point to start the server
ENTRYPOINT ["python", "/app/handler.py"]

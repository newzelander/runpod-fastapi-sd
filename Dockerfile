# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app/

# Install the necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable to prevent buffering
ENV PYTHONUNBUFFERED 1

# Run the main.py file by default when starting the container
ENTRYPOINT ["python", "/app/main.py"]

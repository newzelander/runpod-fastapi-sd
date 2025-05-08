# Use the official Python 3.8 image as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the local files into the container
COPY . /app

# Install Python dependencies from requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Command to run your application
CMD ["python", "handler.py"]

# Use a Python base image
FROM python:3.10-slim

# Set up working directory
WORKDIR /app

# Copy the Python script and requirements.txt into the container
COPY preload_model.py /app/preload_model.py
COPY requirements.txt /app/requirements.txt

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the preload_model.py script
CMD ["python", "preload_model.py"]

FROM python:3.10-slim

WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Add a simple debug statement to confirm the Docker container is running
RUN echo "Starting the container..."

# Start the app using Python
CMD ["python", "runpod_handler.py"]

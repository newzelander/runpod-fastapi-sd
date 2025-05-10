FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the necessary files into the container
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the handler when the container starts
CMD ["python", "handler.py"]

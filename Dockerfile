FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the necessary files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable to disable Hugging Face cache
ENV HF_HUB_DISABLE_CACHE=1

# Expose the port for the application
EXPOSE 8080

# Run the handler when the container starts
CMD ["python", "handler.py"]

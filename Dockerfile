FROM python:3.10-slim

# Install basic dependencies
RUN apt-get update && apt-get install -y git

# Install Python libraries
RUN pip install --no-cache-dir runpod diffusers transformers accelerate torch torchvision safetensors

# Copy your handler
COPY runpod_handler.py /runpod_handler.py

# Set the command for runpod
CMD ["python3", "/runpod_handler.py"]

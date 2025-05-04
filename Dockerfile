FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY . .

# Required env for huggingface caching (optional)
ENV HF_HOME=/runpod-volume/.cache/huggingface
ENV TRANSFORMERS_CACHE=/runpod-volume/.cache/huggingface/transformers
ENV HF_HUB_CACHE=/runpod-volume/.cache/huggingface/hub

CMD ["python", "handler.py"]

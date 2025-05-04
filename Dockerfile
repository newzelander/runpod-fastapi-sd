FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    libpython3.10-dev \
    build-essential \
    git \
    curl \
    libatlas-base-dev \
    libomp-dev

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script for downloading the model
COPY download_model.py .

# Optionally, set the Hugging Face token as an environment variable (can also pass via runtime)
# ENV HUGGING_FACE_HUB_TOKEN=your_token_here

# Set the command to run the Python script
CMD ["python", "download_model.py"]

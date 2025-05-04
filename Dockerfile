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

# Copy the handler script and model download script
COPY handler.py .
COPY download_model.py .

# Set the command to run the handler script
CMD ["python", "handler.py"]

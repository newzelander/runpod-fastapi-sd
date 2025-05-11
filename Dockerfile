FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system-level dependencies required by Pillow, OpenVINO, etc.
RUN apt-get update && apt-get install -y \
    git \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy your app files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install OpenVINO for optimum
RUN pip install --no-cache-dir "optimum[openvino]"


# Default command to run your app
CMD ["python", "handler.py"]

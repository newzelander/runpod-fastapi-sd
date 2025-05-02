FROM python:3.10-slim

# Set environment variable to prevent python output buffering
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install required libraries
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary Python files
COPY preload_model.py /app/
COPY main.py /app/
COPY symlink_tree.py /app/   # NEW line

# Set entrypoint to run the main script
ENTRYPOINT ["python", "/app/main.py"]

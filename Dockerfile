FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Set environment vars
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip git && \
    ln -s /usr/bin/python3 /usr/bin/python

# Install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy code
COPY . /app
WORKDIR /app

# Expose the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.10-slim

WORKDIR /app

# Copy source files
COPY delete_volume.py /app/
COPY main.py /app/

# Install only what's needed
RUN pip install --no-cache-dir runpod

# Set entrypoint
ENTRYPOINT ["python", "/app/main.py"]

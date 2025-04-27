# Dockerfile

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all code
COPY . .

# Run the handler (main.py is auto-imported by runpod_handler.py)
CMD ["python", "runpod_handler.py"]

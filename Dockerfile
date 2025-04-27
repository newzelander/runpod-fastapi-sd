# Dockerfile

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt . 
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all code
COPY . .

# Run the preload_model.py script to download and flatten the model
CMD ["python", "preload_model.py"]

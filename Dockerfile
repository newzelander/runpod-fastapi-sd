FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt . 
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the code
COPY . . 

# Ensure preload_model.py runs first, then runpod_handler.py
CMD ["sh", "-c", "python preload_model.py && python runpod_handler.py"]

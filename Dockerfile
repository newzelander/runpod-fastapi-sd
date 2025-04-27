# Use the official Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy your application code into the container
COPY . .

# Set the entrypoint for the container (assuming runpod_handler.py is your entry point)
CMD ["python", "runpod_handler.py"]
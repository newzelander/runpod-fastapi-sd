FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Optimum with OpenVINO backend
RUN pip install --no-cache-dir "optimum[openvino]" --upgrade

# Run the handler on container start
CMD ["python", "handler.py"]

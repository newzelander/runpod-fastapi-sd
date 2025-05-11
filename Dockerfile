FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the necessary files into the container
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install OpenVINO and related dependencies for optimum
RUN pip install --no-cache-dir "optimum[openvino]" --upgrade



# Run the handler when the container starts
CMD ["python", "handler.py"]

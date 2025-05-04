FROM python:3.10-slim

WORKDIR /app

# Install dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the handler script to the container
COPY handler.py .

# Ensure the environment variables are set (e.g., HF_TOKEN)
# You can override this when running the container using the -e flag if needed
ENV HF_TOKEN=your_huggingface_token_here

# Start the script directly
CMD ["python", "handler.py"]

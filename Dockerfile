FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo "Starting the container..."

# Run both FastAPI + RunPod handler at the same time
CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & python runpod_handler.py"]

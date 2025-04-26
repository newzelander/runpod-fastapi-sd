FROM python:3.10-slim

WORKDIR /app

# Install only runpod
RUN pip install runpod

COPY runpod_handler.py .

CMD ["python", "runpod_handler.py"]

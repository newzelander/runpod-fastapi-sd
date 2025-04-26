FROM python:3.10-slim

WORKDIR /app

COPY . .

CMD ["python", "runpod_handler.py"]

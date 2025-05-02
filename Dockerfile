FROM python:3.10-slim

WORKDIR /app

COPY delete_volume.py /app/
COPY main.py /app/

RUN pip install runpod

ENTRYPOINT ["python", "/app/main.py"]

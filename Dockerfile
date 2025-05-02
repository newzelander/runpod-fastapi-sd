FROM python:3.10-slim

WORKDIR /app

COPY delete_volume.py /app/delete_volume.py

ENTRYPOINT ["python", "/app/delete_volume.py"]

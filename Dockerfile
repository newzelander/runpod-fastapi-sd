FROM python:3.10-slim

# No environment variables needed unless you want unbuffered output
WORKDIR /app

COPY delete_volume.py /app/delete_volume.py

ENTRYPOINT ["python", "delete_volume.py"]

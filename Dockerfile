FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY preload_model.py /app/
COPY main.py /app/
COPY symlink_tree.py /app/   # NEW line

ENTRYPOINT ["python", "/app/main.py"]

# -------- Stage 1: Public Model Image --------
FROM python:3.10-slim AS model-stage

RUN apt-get update && \
    apt-get install -y git git-lfs && \
    git lfs install

RUN git lfs install && \
    git clone https://huggingface.co/stabilityai/stable-diffusion-3.5-large /model

# -------- Stage 2: Private App Image --------
FROM python:3.10-slim

WORKDIR /app

COPY --from=model-stage /model /app/models/sd3.5

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["python", "runpod_handler.py"]

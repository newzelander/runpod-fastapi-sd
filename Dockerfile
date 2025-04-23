# -------- Stage 1: Public Model Image (you build & push this once) --------
FROM python:3.10-slim AS model-stage

RUN apt-get update && \
    apt-get install -y git git-lfs && \
    git lfs install

# Clone model from Hugging Face
RUN git clone https://huggingface.co/stabilityai/stable-diffusion-3.5-large /model

# -------- Stage 2: Private App Image (only you push this) --------
FROM python:3.10-slim

WORKDIR /app

# Copy model from the public image (avoid cloning at runtime)
COPY --from=model-stage /model /app/models/sd3.5

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code (FastAPI, RunPod handler, etc.)
COPY . .

# Expose the port if needed (optional for local testing)
EXPOSE 3000

CMD ["python", "runpod_handler.py"]

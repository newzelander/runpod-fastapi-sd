# -------- Stage 1: Public Model Image (you build & push this once) --------
FROM python:3.10-slim as model-stage

# Install Git, Git LFS, and clone Stable Diffusion model
RUN apt-get update && \
    apt-get install -y git git-lfs && \
    git lfs install

# Clone the model from Hugging Face
RUN git clone https://huggingface.co/stabilityai/stable-diffusion-3.5-large /model

# -------- Stage 2: Private App Image --------
FROM python:3.10-slim

WORKDIR /app

# Copy model from public image
COPY --from=model-stage /model /app/models/sd3.5

# Install app dependencies
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code (FastAPI app, runpod handler, etc.)
COPY . .

# Command to start the app
CMD ["python", "runpod_handler.py"]

# -------- Stage 1: Public Model Image --------
FROM python:3.10-slim AS model-stage

# Install dependencies for cloning the model
RUN apt-get update && \
    apt-get install -y git git-lfs && \
    git lfs install

# Clone the Stable Diffusion model into /model using the token (Hugging Face Token inserted)
RUN git lfs install && \
    git clone https://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@huggingface.co/stabilityai/stable-diffusion-3.5-large /model

# -------- Stage 2: Private App Image --------
FROM python:3.10-slim

WORKDIR /app

# Copy model from the public model image
COPY --from=model-stage /model /app/models/sd3.5

# Install dependencies for your app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code
COPY . .

# Expose the port the app will run on
EXPOSE 3000

# Run the app
CMD ["python", "runpod_handler.py"]

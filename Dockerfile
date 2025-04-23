# -------- Stage 1: Public Model Image --------
FROM python:3.10-slim AS model-stage

# Install dependencies for cloning the model
RUN apt-get update && \
    apt-get install -y git git-lfs && \
    git lfs install

# Set Hugging Face token as an environment variable (safer)
ENV HUGGINGFACE_TOKEN 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

# Use Git's credential helper to authenticate with Hugging Face
RUN git config --global credential.helper store && \
    echo "https://$HUGGINGFACE_TOKEN:@huggingface.co" > ~/.git-credentials && \
    git clone https://huggingface.co/stabilityai/stable-diffusion-3.5-large /model

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

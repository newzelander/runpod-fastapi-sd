# -------- Stage 1: Public Model Image (you build & push this once) --------
FROM python:3.10-slim AS model-stage

# Install Git, Git LFS, and clone Stable Diffusion model
RUN apt-get update && \
    apt-get install -y git git-lfs && \
    git lfs install

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

# Copy entrypoint script that will use the token at runtime
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Command to start the app (run the entrypoint script)
CMD ["/app/entrypoint.sh"]

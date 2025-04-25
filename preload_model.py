from diffusers import StableDiffusion3Pipeline
import os

# Define the correct path for RunPod Serverless persistent volume
model_path = "/runpod-volume/models/stable-diffusion-3.5"

def download_model():
    # Pre-download and cache the model (this will only happen once)
    print("⬇️ Downloading Stable Diffusion 3.5 model...")
    StableDiffusion3Pipeline.from_pretrained(
        "stabilityai/stable-diffusion-3.5",
        cache_dir=model_path
    )
    print(f"✅ Model downloaded and cached at {model_path}")

if __name__ == "__main__":
    download_model()

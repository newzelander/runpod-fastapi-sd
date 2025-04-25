from diffusers import StableDiffusion3Pipeline
import os
import time

# Define the correct path for RunPod Serverless persistent volume
model_path = "/runpod-volume/models/stable-diffusion-3.5"

def download_model():
    # Log the start of the model download process
    print("⬇️ Downloading Stable Diffusion 3.5 model...")
    
    # Make sure the directory exists before downloading
    os.makedirs(model_path, exist_ok=True)

    try:
        # Download and cache the model
        StableDiffusion3Pipeline.from_pretrained(
            "stabilityai/stable-diffusion-3.5",
            cache_dir=model_path
        )
        print(f"✅ Model downloaded and cached at {model_path}")

        # Add sleep to simulate a realistic download time
        time.sleep(5)  # Simulating a 5-second download for debugging

    except Exception as e:
        print(f"❌ Error during model download: {e}")

if __name__ == "__main__":
    download_model()

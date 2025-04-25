import os
import logging
import time
from diffusers import StableDiffusionPipeline

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Define the correct path for RunPod Serverless persistent volume
model_path = "/runpod-volume/models/stable-diffusion-3.5-large"

def download_model():
    try:
        logger.info("⬇️ Downloading Stable Diffusion 3.5 Large model...")
        
        # Simulate delay for debugging
        time.sleep(5)
        
        # Pre-download and cache the model (this will only happen once)
        model = StableDiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-3.5-large",
            cache_dir=model_path
        )
        
        logger.info(f"✅ Model downloaded and cached at {model_path}")
        
    except Exception as e:
        logger.error(f"❌ Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    download_model()

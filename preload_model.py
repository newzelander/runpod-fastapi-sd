import os
import logging
import shutil
from diffusers import StableDiffusion3Pipeline

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Define the correct path for RunPod Serverless persistent volume
model_path = "/runpod-volume/models/stable-diffusion-3.5-large"
snapshot_base_path = os.path.join(model_path, "models--stabilityai--stable-diffusion-3.5-large", "snapshots")
final_model_path = model_path  # Use the root folder for the model files

def download_and_flatten_model():
    try:
        logger.info("⬇️ Downloading Stable Diffusion 3.5 Large model...")

        # Cache the model from Huggingface (this may be slow!)
        model = StableDiffusion3Pipeline.from_pretrained(
            "stabilityai/stable-diffusion-3.5-large",
            cache_dir=model_path
        )

        # Hugging Face saves the model in nested directories. We need to flatten it.
        snapshot_folders = os.listdir(snapshot_base_path)
        assert len(snapshot_folders) > 0, "❌ No snapshot folders found!"
        snapshot_folder = os.path.join(snapshot_base_path, snapshot_folders[0])

        logger.info(f"🔍 Found snapshot folder: {snapshot_folder}")

        # Move files from the snapshot folder to the final destination (flatten)
        for item in os.listdir(snapshot_folder):
            src = os.path.join(snapshot_folder, item)
            dst = os.path.join(final_model_path, item)
            if os.path.isdir(src):
                shutil.move(src, dst)  # Move the directory
            else:
                shutil.move(src, dst)  # Move the file

        logger.info("✅ Model downloaded and flattened successfully!")

        # Return final path for further use (image generation later)
        return final_model_path

    except Exception as e:
        logger.error(f"❌ Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    model_path = download_and_flatten_model()
    logger.info(f"✅ Model is ready at {model_path}")

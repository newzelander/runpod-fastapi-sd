import os
import logging
import shutil
from diffusers import StableDiffusionPipeline  # Adjust based on your exact model

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Define the path for RunPod Serverless persistent volume
runpod_volume_path = "/runpod-volume"
model_path = os.path.join(runpod_volume_path, "models", "stable-diffusion-3.5-large")
snapshot_base_path = os.path.join(model_path, "models--stabilityai--stable-diffusion-3.5-large", "snapshots")
final_model_path = model_path  # Use the root folder for the model files

def delete_all_files_from_volume(volume_path):
    """Delete all files and directories from the specified volume."""
    try:
        logger.info(f"🗑️ Deleting all files from the volume: {volume_path}")
        
        # Recursively remove all files and folders from the volume
        for root, dirs, files in os.walk(volume_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                os.remove(file_path)
            for name in dirs:
                dir_path = os.path.join(root, name)
                os.rmdir(dir_path)
        
        logger.info("✅ All files have been deleted from the volume.")
    except Exception as e:
        logger.error(f"❌ Error occurred while deleting files: {str(e)}")
        raise

def download_and_flatten_model():
    try:
        logger.info("⬇️ Downloading Stable Diffusion 3.5 Large model...")

        # Cache the model from Huggingface (this may be slow!)
        model = StableDiffusionPipeline.from_pretrained(
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
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

        logger.info("✅ Model downloaded and flattened successfully!")

        # Return final path for further use (image generation later)
        return final_model_path

    except Exception as e:
        logger.error(f"❌ Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    # First, delete all files from the entire /runpod-volume/ directory
    delete_all_files_from_volume(runpod_volume_path)
    
    # Then download and flatten the model
    model_path = download_and_flatten_model()
    logger.info(f"✅ Model is ready at {model_path}")

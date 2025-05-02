import os
import logging
import shutil
from diffusers import StableDiffusion3Pipeline

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def clear_volume(model_path):
    logger.info("⬇️ Clearing the persistent volume...")
    try:
        for item in os.listdir(model_path):
            item_path = os.path.join(model_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        logger.info("✅ Volume cleared successfully!")
    except Exception as e:
        logger.error(f"❌ Error clearing volume: {str(e)}")
        raise

def download_and_flatten_model(model_path, snapshot_base_path, final_model_path):
    try:
        logger.info("⬇️ Downloading Stable Diffusion 3.5 Large model...")
        model = StableDiffusion3Pipeline.from_pretrained(
            "stabilityai/stable-diffusion-3.5-large",
            cache_dir=model_path
        )

        snapshot_folders = os.listdir(snapshot_base_path)
        assert len(snapshot_folders) > 0, "❌ No snapshot folders found!"
        snapshot_folder = os.path.join(snapshot_base_path, snapshot_folders[0])
        logger.info(f"🔍 Found snapshot folder: {snapshot_folder}")

        for item in os.listdir(snapshot_folder):
            src = os.path.join(snapshot_folder, item)
            dst = os.path.join(final_model_path, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

        logger.info("✅ Model downloaded and flattened successfully!")
        return final_model_path
    except Exception as e:
        logger.error(f"❌ Error occurred during download and flattening: {str(e)}")
        raise

# 👇 This is the actual handler RunPod will call
def handler(job):
    logger.info(f"📦 Received job: {job}")
    model_path = "/runpod-volume/models/stable-diffusion-3.5-large"
    snapshot_base_path = os.path.join(model_path, "models--stabilityai--stable-diffusion-3.5-large", "snapshots")
    final_model_path = model_path

    clear_volume(model_path)
    result_path = download_and_flatten_model(model_path, snapshot_base_path, final_model_path)

    return {"status": "done", "model_path": result_path}

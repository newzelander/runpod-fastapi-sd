import os
import shutil
import logging
from huggingface_hub import snapshot_download, login

# Set up logging for maximum verbosity
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# Helper to get disk usage stats for /runpod-volume
def get_volume_disk_usage(path="/runpod-volume"):
    total, used, free = shutil.disk_usage(path)
    logger.debug(f"Disk usage - Total: {total} bytes, Used: {used} bytes, Free: {free} bytes")
    return {
        "total_gb": round(total / (1024 ** 3), 2),
        "used_gb": round(used / (1024 ** 3), 2),
        "free_gb": round(free / (1024 ** 3), 2)
    }

# Safely clear the contents of /runpod-volume without removing the mount point
def clear_runpod_volume():
    folder = "/runpod-volume"
    logger.debug("Clearing /runpod-volume...")
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # remove file or link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # remove directory
        except Exception as e:
            logger.error(f"Failed to delete {file_path}. Reason: {e}")

def handler(event, context):
    logger.info("Handler invoked")

    # Extract input parameters from the event
    inputs = event.get("input", {})
    model_name = inputs.get("model")
    cache_dir = inputs.get("cache_directory", "/runpod-volume/huggingface-cache")
    max_disk_usage = float(inputs.get("max_disk_usage", 0.9))
    check_disk_space = inputs.get("check_disk_space", True)

    if not model_name:
        logger.error("Error: Missing 'model' in input.")
        return {"error": "Missing 'model' in input."}

    logger.info(f"Received model name: {model_name}")
    logger.info(f"Cache directory: {cache_dir}")
    logger.info(f"Max disk usage threshold: {max_disk_usage * 100}%")
    
    # Clean up the persistent volume if required
    logger.info("Clearing /runpod-volume...")
    clear_runpod_volume()

    # Check disk space before downloading
    if check_disk_space:
        usage = shutil.disk_usage("/runpod-volume")
        used_percentage = usage.used / usage.total
        logger.info(f"Current disk usage: {used_percentage * 100}%")
        if used_percentage > max_disk_usage:
            logger.error("Error: Disk usage exceeds limit before download.")
            return {"error": "Disk usage exceeds limit before download. Volume has been cleared."}

    try:
        # Log into Hugging Face
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            logger.error("Error: HF_TOKEN is not set.")
            return {"error": "HF_TOKEN is not set."}

        logger.info("Logging in to Hugging Face...")
        login(token=hf_token)

        logger.info(f"Downloading model: {model_name}")
        model_path = snapshot_download(
            repo_id=model_name,
            cache_dir=cache_dir,
            local_files_only=False,
            resume_download=True
        )

        logger.info(f"Model downloaded successfully to: {model_path}")

        # After download, report how much space is used
        disk_usage = get_volume_disk_usage()

        return {
            "status": "Download complete",
            "model_path": model_path,
            "disk_usage": disk_usage
        }

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {"error": str(e)}


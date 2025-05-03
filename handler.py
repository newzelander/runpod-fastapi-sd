from preload_model import get_or_download_model

# Just define the base cache path (no nested copying)
CACHE_DIR = "/runpod-volume/models"

def handler(event):
    model_path = get_or_download_model(CACHE_DIR)

    return {
        "status": "ready",
        "model_path": model_path
    }

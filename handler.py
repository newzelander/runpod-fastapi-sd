from preload_model import get_or_download_model

def handler(event):
    model_path = get_or_download_model()
    return {
        "status": "ready",
        "model_path": model_path
    }

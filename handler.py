import os
from preload_model import download_model

model_path = "/runpod-volume/models/stable-diffusion-3.5-large"

def handler(event):
    download_model(model_path)
    return {
        "status": "ready",
        "model_path": model_path
    }

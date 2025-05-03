import os
from preload_model import download_model

MODEL_DIR = "/runpod-volume/models/stable-diffusion-3.5-large"

def handler(event):
    download_model(MODEL_DIR)
    return {
        "status": "model ready",
        "model_dir": MODEL_DIR
    }

import os
from preload_model import download_model
from symlink_tree import symlink_tree

def handler(event):
    model_path = "/tmp/models/stable-diffusion-3.5-large"
    inference_path = "/tmp/inference_model"

    # Download model if needed
    download_model(model_path)

    # Symlink it for use
    symlink_tree(model_path, inference_path)

    return {
        "status": "ready",
        "model_dir": inference_path
    }

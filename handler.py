import os
from preload_model import download_model
from symlink_tree import symlink_tree

model_path = "/tmp/models/stable-diffusion-3.5-large"
inference_path = "/tmp/inference_model"

# Download the model if it's not already present
download_model(model_path)

# Create symlinks to simplify access for inference
symlink_tree(model_path, inference_path)

def handler(event):
    return {
        "status": "ready",
        "model_dir": inference_path
    }

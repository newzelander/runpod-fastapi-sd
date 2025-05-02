import os
from preload_model import download_model
from symlink_tree import symlink_tree

# Correct model path and inference path
model_path = "/runpod-volume/models/stable-diffusion-3.5-large"  # The folder to download and store the model
inference_path = "/runpod-volume/inference_model"  # The path for symlinks that point to the correct model files

# Download the model if it's not already present
download_model(model_path)

# Create symlinks to simplify access for inference
symlink_tree(model_path, inference_path)

def handler(event):
    return {
        "status": "ready",
        "model_dir": inference_path  # This is the symlinked path to the actual model
    }

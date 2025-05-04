import os
import shutil
import torch
from huggingface_hub import hf_hub_download
from transformers import AutoModel
import runpod
import psutil

# Define paths
cache_dir = "/runpod-volume/huggingface-cache/stable-diffusion-3.5-large"
model_name = "stabilityai/stable-diffusion-3.5-large"

# Retrieve the HF_TOKEN environment variable
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set.")

# Function to check disk space
def check_disk_space(threshold=0.90):
    total, used, free = shutil.disk_usage("/")
    disk_usage = used / total
    print(f"Disk usage: {disk_usage * 100:.2f}%")
    return disk_usage < threshold

# Function to download the model
def download_model():
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Check if model already exists to prevent redundant download
    model_path = os.path.join(cache_dir, model_name.split("/")[-1])
    if os.path.exists(model_path):
        print(f"Model already exists at {model_path}. Skipping download.")
        return model_path

    # If space is sufficient, download model
    if check_disk_space():
        print("Sufficient space available. Downloading model...")
        hf_hub_download(repo_id=model_name, token=hf_token, cache_dir=cache_dir)
        print(f"Model downloaded successfully to {model_path}.")
        return model_path
    else:
        print("Disk quota exceeded. Deleting model and not downloading again.")
        # Delete all cached files in the cache directory
        shutil.rmtree(cache_dir)
        return None

# Run the model download
download_model()

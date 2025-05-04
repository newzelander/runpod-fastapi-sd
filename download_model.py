import os
import shutil
import requests
import torch
from huggingface_hub import hf_hub_download
import subprocess

# Function to get the disk usage of the specific directory
def get_disk_usage(path):
    total, used, free = shutil.disk_usage(path)
    return used / total

# Function to download the model
def download_model():
    model_name = "stabilityai/stable-diffusion-3.5-large"
    cache_directory = "/runpod-volume/huggingface-cache/stable-diffusion-3.5-large"
    hf_token = os.environ.get("HF_TOKEN")

    if not hf_token:
        raise ValueError("HF_TOKEN environment variable is not set.")
    
    print("Starting download...")
    
    # Delete everything in the persistent volume before starting the download
    if os.path.exists(cache_directory):
        print(f"Deleting previous data in {cache_directory}")
        shutil.rmtree(cache_directory)

    os.makedirs(cache_directory, exist_ok=True)

    # Check disk space before downloading
    disk_usage = get_disk_usage("/runpod-volume")
    if disk_usage > 0.9:
        print("Disk space usage exceeds 90%. Aborting download.")
        return {"error": "Disk space exceeded"}

    # Download the model using Hugging Face API
    print(f"Downloading model: {model_name}")
    model_path = hf_hub_download(repo_id=model_name, token=hf_token, cache_dir=cache_directory)

    # Check space after download
    used_space = get_disk_usage("/runpod-volume") * 100
    print(f"Download complete. Disk usage: {used_space:.2f}% used.")

    return {"model_path": model_path, "disk_usage": used_space}


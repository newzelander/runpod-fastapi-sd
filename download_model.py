import os
import shutil
from huggingface_hub import hf_hub_download

# Define paths
volume_dir = "/runpod-volume"
cache_dir = os.path.join(volume_dir, "huggingface-cache")
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

# Function to clear the volume directory
def clear_volume():
    print("Clearing /runpod-volume directory...")
    if os.path.exists(volume_dir):
        shutil.rmtree(volume_dir)
    os.makedirs(volume_dir)  # Recreate the volume directory

# Function to show disk space usage
def show_disk_usage():
    total, used, free = shutil.disk_usage("/")
    print(f"Total disk space: {total // (2**30)} GB")
    print(f"Used disk space: {used // (2**30)} GB")
    print(f"Free disk space: {free // (2**30)} GB")
    print(f"Current disk usage: {used / total * 100:.2f}%")

# Function to download the model
def download_model():
    # Clear everything from /runpod-volume
    clear_volume()

    # Check if there is sufficient space before starting the download
    if not check_disk_space():
        print("Disk quota exceeded. Not downloading the model.")
        return None

    print("Sufficient space available. Starting download...")

    # Download the model to the cache directory
    model_path = hf_hub_download(repo_id=model_name, token=hf_token, cache_dir=cache_dir)
    print(f"Model downloaded successfully to {model_path}.")

    # Show disk space after downloading the model
    show_disk_usage()

    return model_path

# Run the model download
download_model()

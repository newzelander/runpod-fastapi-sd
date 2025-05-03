import os
import shutil
from huggingface_hub import snapshot_download
import psutil

MODEL_ID = "stabilityai/stable-diffusion-3.5-large"
CACHE_DIR = "/runpod-volume/models/hf-cache"

def get_disk_usage():
    # Get the disk usage stats
    usage = psutil.disk_usage('/')
    return usage

def clear_cache():
    # Remove the entire cache directory
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
        print(f"Cache at {CACHE_DIR} has been cleared.")
    else:
        print("Cache directory does not exist.")

def get_or_download_model():
    # Get Hugging Face token from environment
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN is not set.")
    
    try:
        # Attempt to download model snapshot to cache
        snapshot_path = snapshot_download(
            repo_id=MODEL_ID,
            cache_dir=CACHE_DIR,
            use_auth_token=hf_token,
            ignore_patterns=["*.msgpack"],  # Optional: skip unneeded files
            local_dir_use_symlinks=True,
        )
        return snapshot_path
    
    except OSError as e:
        if "Disk quota exceeded" in str(e):
            # Print the disk usage details when the error occurs
            usage = get_disk_usage()
            print(f"Disk usage: {usage.percent}% used out of {usage.total / (1024**3):.2f} GB total.")
            print(f"Free space: {usage.free / (1024**3):.2f} GB.")
            
            # Clear the cache to free up space
            clear_cache()
            
            # Do not attempt to download again as per your request
            print("Disk quota exceeded. Cache cleared, but no download will be attempted.")
            return None
        else:
            # Raise the error if it's not a "Disk quota exceeded" error
            raise e

# Entry point to get or download the model
if __name__ == "__main__":
    get_or_download_model()

from huggingface_hub import snapshot_download
import os
import shutil
import subprocess

MODEL_ID = "stabilityai/stable-diffusion-3.5-large"
CACHE_DIR = "/runpod-volume/models/hf-cache"

def get_disk_usage():
    """Function to check disk usage"""
    try:
        # Run df command to get disk space details
        result = subprocess.check_output(["df", "-h", CACHE_DIR])
        # Get the output and print it
        print("Disk usage for CACHE_DIR:")
        print(result.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error while checking disk usage: {e}")
        
def clear_cache():
    """Function to clear the cache directory"""
    try:
        print(f"Clearing cache in {CACHE_DIR}...")
        shutil.rmtree(CACHE_DIR)
        print("Cache cleared successfully.")
    except Exception as e:
        print(f"Error while clearing cache: {e}")

def get_or_download_model():
    # Get Hugging Face token from environment
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN is not set.")

    try:
        # Try downloading model snapshot to cache
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
            print("Disk quota exceeded error detected.")
            # Display disk usage before clearing cache
            get_disk_usage()
            # Clear the cache to free up space
            clear_cache()
            # Do not attempt to download the model again after clearing cache
            print("Cache cleared. Exiting the process.")
            return None  # Indicating that the download was not successful

# Example usage
get_or_download_model()

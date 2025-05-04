import subprocess
import os
import shutil
import time
import sys
from huggingface_hub import login, snapshot_download

# The path to the directory where the model files should be saved
HF_CACHE_DIR = "/runpod-volume/hf-cache"
TARGET_DIR = "/runpod-volume"

# Function to authenticate with Hugging Face
def authenticate():
    try:
        HF_TOKEN = os.getenv("HF_TOKEN")  # Secure: use env var
        if not HF_TOKEN:
            raise ValueError("Hugging Face token not found. Set HF_TOKEN environment variable.")
        login(token=HF_TOKEN)
        print("[AUTH] Hugging Face login successful.")
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        sys.exit(1)

# Helper function to check the available disk space of /runpod-volume
def get_persistent_disk_usage():
    try:
        result = subprocess.check_output(['df', '-h', '/runpod-volume']).decode('utf-8')
        for line in result.splitlines():
            if '/runpod-volume' in line:
                parts = line.split()
                total = parts[1]
                used = parts[2]
                available = parts[3]
                return total, used, available
        return None, None, None
    except Exception as e:
        print(f"[ERROR] Disk usage check failed: {e}")
        return None, None, None

# Function to clean the /runpod-volume directory, excluding hf-cache
def clean_runpod_volume():
    try:
        print(f"[ACTION] Cleaning up {TARGET_DIR} (excluding hf-cache)...")
        for item in os.listdir(TARGET_DIR):
            item_path = os.path.join(TARGET_DIR, item)
            if item_path != HF_CACHE_DIR:
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as cleanup_error:
                    print(f"[WARNING] Could not remove {item_path}: {cleanup_error}")
        print(f"[SUCCESS] {TARGET_DIR} cleaned.")
    except Exception as e:
        print(f"[ERROR] Failed to clean {TARGET_DIR}: {e}")

# Function to download the model
def download_model(model_name):
    try:
        print(f"[STEP] Downloading model: {model_name} ...")
        snapshot_download(
            repo_id=model_name,
            cache_dir=HF_CACHE_DIR,
            local_dir=HF_CACHE_DIR,
            local_dir_use_symlinks=False,
            revision="main"
        )
        print(f"[SUCCESS] Model {model_name} downloaded successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to download model: {e}")

# Main function
def main(model_name):
    print("[START] RUN_SYNC_TRIGGERED is true. Starting script.")

    # Step 1: Authenticate with Hugging Face
    authenticate()

    # Step 2: Check disk usage
    total, used, available = get_persistent_disk_usage()
    if total and available:
        print(f"[DISK] Total: {total}")
        print(f"[DISK] Used: {used}")
        print(f"[DISK] Free: {available}")
    else:
        print("[ERROR] Could not retrieve disk space information.")

    # Step 3: Clean the volume (excluding hf-cache)
    clean_runpod_volume()

    # Step 4: Download the model
    download_model(model_name)

    # Step 5: Verify download
    if os.path.exists(HF_CACHE_DIR):
        model_files = os.listdir(HF_CACHE_DIR)
        print(f"[INFO] Total files in {HF_CACHE_DIR}: {len(model_files)}")
    else:
        print(f"[ERROR] hf-cache directory does not exist.")

# Run the script
if __name__ == "__main__":
    # Replace with your actual model
    model_name = "stabilityai/stable-diffusion-3.5-large"
    main(model_name)

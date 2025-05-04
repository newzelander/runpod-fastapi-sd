import subprocess
import os
import shutil
import time
import sys
import huggingface_hub

# The path to the directory where the model files should be saved
HF_CACHE_DIR = "/runpod-volume/hf-cache"
TARGET_DIR = "/runpod-volume"

# Helper function to check the available disk space of /runpod-volume
def get_persistent_disk_usage():
    try:
        # Running `df -h` to get disk usage info for /runpod-volume
        result = subprocess.check_output(['df', '-h', '/runpod-volume']).decode('utf-8')
        # Extracting relevant disk information from the result
        for line in result.splitlines():
            if '/runpod-volume' in line:
                parts = line.split()
                total = parts[1]  # Total space
                used = parts[2]   # Used space
                available = parts[3]  # Available space
                return total, used, available
        return None, None, None
    except Exception as e:
        print(f"Error getting disk usage: {e}")
        return None, None, None

# Function to clean the /runpod-volume directory, excluding hf-cache
def clean_runpod_volume():
    try:
        print(f"[ACTION] Cleaning up {TARGET_DIR} (including hf-cache)...")
        # Delete everything except hf-cache
        for root, dirs, files in os.walk(TARGET_DIR, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                if HF_CACHE_DIR not in file_path:
                    os.remove(file_path)
            for name in dirs:
                dir_path = os.path.join(root, name)
                if HF_CACHE_DIR not in dir_path:
                    shutil.rmtree(dir_path)
        print(f"[SUCCESS] {TARGET_DIR} cleaned.")
    except Exception as e:
        print(f"[ERROR] Failed to clean {TARGET_DIR}: {e}")

# Function to download the model
def download_model(model_name):
    try:
        print(f"[STEP] Downloading model {model_name}...")
        # Assuming huggingface_hub.download_url works correctly and does not conflict with symlinks
        huggingface_hub.snapshot_download(model_name, cache_dir=HF_CACHE_DIR)
        print(f"[INFO] Model {model_name} downloaded successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to download model: {e}")

# Main function
def main(model_name):
    print(f"[START] RUN_SYNC_TRIGGERED is true. Starting script.")

    # Get disk usage information for /runpod-volume
    total, used, available = get_persistent_disk_usage()

    if total and available:
        print(f"[DISK] Total: {total}")
        print(f"[DISK] Used: {used}")
        print(f"[DISK] Free: {available}")
    else:
        print("[ERROR] Could not retrieve disk space information.")

    # Clean up the volume (including hf-cache) before starting the download
    clean_runpod_volume()

    # Download the model
    download_model(model_name)

    # Checking if the model was downloaded (files in hf-cache directory)
    model_files = os.listdir(HF_CACHE_DIR)
    if len(model_files) > 0:
        print(f"[INFO] Total files in {HF_CACHE_DIR}: {len(model_files)}")
    else:
        print(f"[INFO] No files found in {HF_CACHE_DIR}, model might not have been downloaded correctly.")

# Run the script
if __name__ == "__main__":
    model_name = "your_model_name_here"  # Replace with your model name
    main(model_name)

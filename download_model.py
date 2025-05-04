import os
import shutil
from huggingface_hub import hf_hub_download
import traceback
import time

# Get Hugging Face token securely
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set.")

# Set Hugging Face cache to persistent directory
os.environ["HF_HOME"] = "/runpod-volume/hf-cache"  # Ensure the cache uses the persistent volume

# Define paths
MODEL_NAME = "stabilityai/stable-diffusion-3.5-large"
TARGET_DIR = "/runpod-volume/stable-diffusion"

# Function to wait until RUN_SYNC_TRIGGERED becomes true
def wait_for_run_sync():
    while True:
        run_sync = os.environ.get("RUN_SYNC_TRIGGERED", "false").lower() == "true"
        if run_sync:
            print("[INFO] RunSync trigger detected. Proceeding with model download...")
            break
        print("[INFO] Waiting for RunSync trigger...")
        time.sleep(5)

# Disk usage and error handling functions
def show_disk_usage():
    total, used, free = shutil.disk_usage("/runpod-volume")
    print(f"[DISK] Total: {total // (2**20)} MB")
    print(f"[DISK] Used: {used // (2**20)} MB")
    print(f"[DISK] Free: {free // (2**20)} MB")

def handle_quota_error():
    print("[ERROR] Disk quota exceeded.")
    print("[ACTION] Showing current disk usage:")
    show_disk_usage()

    print("[ACTION] Cleaning up /runpod-volume to free space...")
    try:
        shutil.rmtree("/runpod-volume")
        os.makedirs("/runpod-volume")
        print("[SUCCESS] Volume cleaned.")
    except Exception as cleanup_err:
        print(f"[FAILURE] Could not clean volume: {cleanup_err}")

    print("[INFO] Exiting without retrying download due to quota issue.")

# Model download function
def download_model():
    if os.path.exists(TARGET_DIR):
        print(f"[INFO] Model already exists at {TARGET_DIR}. Skipping download.")
        return

    os.makedirs(TARGET_DIR, exist_ok=True)
    print(f"[INFO] Downloading model to {TARGET_DIR} using symlinks to save space...")

    try:
        # Download model files and create symlinks
        hf_hub_download(
            repo_id=MODEL_NAME,
            local_dir=TARGET_DIR,
            use_auth_token=hf_token,
            local_dir_use_symlinks=True
        )
        print(f"[SUCCESS] Model downloaded and symlinked to {TARGET_DIR}")
    except OSError as e:
        if "Disk quota exceeded" in str(e):
            handle_quota_error()
        else:
            print("[ERROR] Unexpected OS error:")
            traceback.print_exc()
    except Exception as e:
        print("[ERROR] Unexpected exception occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    wait_for_run_sync()  # Wait until the RunSync button is pressed
    download_model()     # Start downloading the model

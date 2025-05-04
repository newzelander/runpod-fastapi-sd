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

# Flag to indicate whether to run the download process
RUN_SYNC_TRIGGERED = os.environ.get("RUN_SYNC_TRIGGERED", "false") == "true"  # Use this variable to trigger the execution

# Function to simulate waiting for the RunSync trigger
def wait_for_run_sync():
    while not RUN_SYNC_TRIGGERED:
        print("[INFO] Waiting for RunSync trigger...")
        time.sleep(5)  # Sleep and wait for the trigger to be set to true

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
    # Force the download of the model even if it already exists
    print(f"[INFO] Downloading model {MODEL_NAME} to {TARGET_DIR}...")
    os.makedirs(TARGET_DIR, exist_ok=True)

    try:
        hf_hub_download(
            repo_id=MODEL_NAME,
            local_dir=TARGET_DIR,
            use_auth_token=hf_token,
            local_dir_use_symlinks=True
        )
        print(f"[SUCCESS] Model downloaded to {TARGET_DIR}")
    except OSError as e:
        if "Disk quota exceeded" in str(e):
            handle_quota_error()
        else:
            print("[ERROR] Unexpected OS error:")
            traceback.print_exc()
    except Exception:
        print("[ERROR] Unexpected exception occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    wait_for_run_sync()  # Wait until the RunSync button is pressed and triggered
    download_model()  # Download model, even if it exists

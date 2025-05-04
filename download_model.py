import os
import shutil
from huggingface_hub import hf_hub_download
import traceback

# Get Hugging Face token securely
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set.")

# Set persistent Hugging Face cache directory
os.environ["HF_HOME"] = "/runpod-volume/hf-cache"

# Model configuration
MODEL_NAME = "stabilityai/stable-diffusion-3.5-large"
TARGET_DIR = "/runpod-volume/stable-diffusion"

# Disk usage and error handling
def show_disk_usage():
    total, used, free = shutil.disk_usage("/runpod-volume")
    print(f"[DISK] Total: {total // (2**20)} MB")
    print(f"[DISK] Used: {used // (2**20)} MB")
    print(f"[DISK] Free: {free // (2**20)} MB")

def handle_quota_error():
    print("[ERROR] Disk quota exceeded.")
    show_disk_usage()
    try:
        shutil.rmtree("/runpod-volume")
        os.makedirs("/runpod-volume")
        print("[SUCCESS] Volume cleaned.")
    except Exception as cleanup_err:
        print(f"[FAILURE] Could not clean volume: {cleanup_err}")
    print("[INFO] Exiting due to quota issue.")
    exit(1)

# Download model
def download_model():
    if os.path.exists(TARGET_DIR):
        print(f"[INFO] Model already exists at {TARGET_DIR}. Skipping download.")
        return

    os.makedirs(TARGET_DIR, exist_ok=True)
    print(f"[INFO] Downloading model to {TARGET_DIR}...")

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
            print("[ERROR] OS error occurred:")
            traceback.print_exc()
    except Exception as e:
        print("[ERROR] Unexpected exception occurred:")
        traceback.print_exc()

# Main entry point
if __name__ == "__main__":
    download_model()

import os
import shutil
import traceback
import time
from huggingface_hub import hf_hub_download

# Set Hugging Face token and cache path
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set.")

os.environ["HF_HOME"] = "/runpod-volume/hf-cache"

MODEL_NAME = "stabilityai/stable-diffusion-3.5-large"
TARGET_DIR = "/runpod-volume/stable-diffusion"

def show_disk_usage():
    total, used, free = shutil.disk_usage("/runpod-volume")
    print(f"[DISK] Total: {total // (2**20)} MB")
    print(f"[DISK] Used: {used // (2**20)} MB")
    print(f"[DISK] Free: {free // (2**20)} MB")

def handle_quota_error():
    print("[ERROR] Disk quota exceeded.")
    show_disk_usage()
    print("[ACTION] Cleaning up volume...")
    try:
        shutil.rmtree("/runpod-volume")
        os.makedirs("/runpod-volume")
        print("[SUCCESS] Volume cleaned.")
    except Exception as cleanup_err:
        print(f"[FAILURE] Cleanup failed: {cleanup_err}")

def download_model():
    required_files = ["model_index.json"]
    model_ready = all(os.path.exists(os.path.join(TARGET_DIR, f)) for f in required_files)

    if model_ready:
        print(f"[INFO] Model already downloaded at {TARGET_DIR}.")
        return

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
    if os.environ.get("RUNPOD_RUNSYNC") != "true":
        print("[INFO] Not triggered by RunSync. Exiting.")
        exit(0)

    print("[INFO] RunSync trigger detected. Proceeding...")
    download_model()

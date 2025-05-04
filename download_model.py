import os
import shutil
from huggingface_hub import hf_hub_download
import traceback
import time

# 1. Set Hugging Face cache to persistent volume
os.environ["HF_HOME"] = "/runpod-volume/hf-cache"

# 2. Get Hugging Face token from env
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set.")

# 3. Set target directory for model
TARGET_DIR = "/runpod-volume/stable-diffusion"

# 4. Wait until RUN_SYNC_TRIGGERED is true
def wait_for_run_sync():
    while os.environ.get("RUN_SYNC_TRIGGERED", "false").lower() != "true":
        print("[INFO] Waiting for RunSync trigger...")
        time.sleep(5)

# 5. Show disk usage
def show_disk_usage():
    total, used, free = shutil.disk_usage("/runpod-volume")
    print(f"[DISK] Total: {total // (2**20)} MB")
    print(f"[DISK] Used: {used // (2**20)} MB")
    print(f"[DISK] Free: {free // (2**20)} MB")

# 6. Clean the target directory
def clean_target_directory():
    if os.path.exists(TARGET_DIR):
        print(f"[INFO] Cleaning target directory: {TARGET_DIR}")
        shutil.rmtree(TARGET_DIR)
    os.makedirs(TARGET_DIR, exist_ok=True)
    print("[INFO] Target directory is clean.")

# 7. Download the model
def download_model():
    print(f"[INFO] Downloading model to {TARGET_DIR}...")
    try:
        hf_hub_download(
            repo_id="stabilityai/stable-diffusion-3.5-large",
            local_dir=TARGET_DIR,
            use_auth_token=hf_token,
            local_dir_use_symlinks=True
        )
        print(f"[SUCCESS] Model downloaded to {TARGET_DIR}")
    except OSError as e:
        if "Disk quota exceeded" in str(e):
            print("[ERROR] Disk quota exceeded.")
            show_disk_usage()
        else:
            print("[ERROR] Unexpected OS error:")
            traceback.print_exc()
    except Exception as e:
        print("[ERROR] Unexpected exception:")
        traceback.print_exc()

# 8. Script entrypoint
if __name__ == "__main__":
    wait_for_run_sync()
    clean_target_directory()
    download_model()

import os
import shutil
import traceback
from huggingface_hub import snapshot_download

# Read environment variables
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set.")

run_sync_triggered = os.environ.get("RUN_SYNC_TRIGGERED", "false").lower() == "true"
if not run_sync_triggered:
    print("[INFO] RUN_SYNC_TRIGGERED is not set to true. Exiting.")
    exit(0)

# Define paths
CACHE_DIR = "/runpod-volume/hf-cache"
TARGET_DIR = "/runpod-volume/stable-diffusion"

# Set Hugging Face cache location
os.environ["HF_HOME"] = CACHE_DIR

def show_disk_usage():
    total, used, free = shutil.disk_usage("/runpod-volume")
    print(f"[DISK] Total: {total // (2**20)} MB")
    print(f"[DISK] Used: {used // (2**20)} MB")
    print(f"[DISK] Free: {free // (2**20)} MB")

def check_files_in_cache(directory):
    total_files = sum([len(files) for r, d, files in os.walk(directory)])
    print(f"[INFO] Total files in {directory}: {total_files}")

def clean_volume():
    print("[ACTION] Cleaning up /runpod-volume to free space (including hf-cache)...")
    try:
        # Deleting everything in /runpod-volume, including hf-cache
        for item in os.listdir("/runpod-volume"):
            item_path = os.path.join("/runpod-volume", item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print("[SUCCESS] /runpod-volume cleaned (hf-cache deleted as well).")
    except Exception as e:
        print(f"[ERROR] Failed to clean /runpod-volume: {e}")

def reset_trigger_flag():
    try:
        os.environ["RUN_SYNC_TRIGGERED"] = "false"
        print("[INFO] RUN_SYNC_TRIGGERED flag reset.")
    except Exception as e:
        print(f"[WARNING] Failed to reset trigger flag: {e}")

def download_model():
    print("[STEP] Downloading model...")

    try:
        check_files_in_cache(CACHE_DIR)

        snapshot_download(
            repo_id="stabilityai/stable-diffusion-3.5-large",
            cache_dir=CACHE_DIR,
            local_dir=TARGET_DIR,  # Download directly into TARGET_DIR, no symlinks
            use_auth_token=hf_token
        )
        print(f"[SUCCESS] Model downloaded to {TARGET_DIR}")
        reset_trigger_flag()
    except OSError as e:
        if "Disk quota exceeded" in str(e):
            print("[ERROR] Disk quota exceeded.")
            show_disk_usage()
            clean_volume()
            print("[INFO] Exiting without retrying download.")
        else:
            print("[ERROR] OSError occurred:")
            traceback.print_exc()
    except Exception:
        print("[ERROR] Unexpected exception occurred:")
        traceback.print_exc()

# Start process
print("[START] RUN_SYNC_TRIGGERED is true. Starting script.")
clean_volume()  # Clean everything, including the cache
download_model()  # Download model

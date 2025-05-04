import os
import shutil
import subprocess
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
    try:
        # Get actual size of /runpod-volume using 'du -sh' command
        output = subprocess.check_output(['du', '-sh', '/runpod-volume']).decode('utf-8')
        
        # Output is like "12G   /runpod-volume"
        size = output.split()[0]
        
        print(f"[DISK] Used space: {size}")
    except Exception as e:
        print(f"[ERROR] Failed to check disk usage: {str(e)}")

def clean_volume():
    print("[ACTION] Cleaning up /runpod-volume (including hf-cache)...")
    try:
        # Clean up everything in /runpod-volume, including the hf-cache folder
        for item in os.listdir("/runpod-volume"):
            item_path = os.path.join("/runpod-volume", item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print("[SUCCESS] /runpod-volume cleaned.")
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
        # Check available disk space before downloading (using subprocess for accurate result)
        show_disk_usage()

        # Ensure there's enough space for the model
        model_size_gb = 26  # Adjust this to the actual model size (in GB)
        
        # You can use the `subprocess` output to calculate the free space and compare
        output = subprocess.check_output(['du', '-sh', '/runpod-volume']).decode('utf-8')
        free_space = output.split()[0]
        
        # Assuming free_space is in GB, adjust parsing if needed (e.g. "12G" or "1.5G")
        if float(free_space[:-1]) < model_size_gb:
            print(f"[ERROR] Not enough free space to download the model.")
            print(f"[INFO] Exiting without retrying download.")
            return

        # Proceed to download the model
        snapshot_download(
            repo_id="stabilityai/stable-diffusion-3.5-large",
            cache_dir=CACHE_DIR,
            use_auth_token=hf_token
        )
        print(f"[SUCCESS] Model downloaded to {CACHE_DIR}")
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
clean_volume()  # Clean everything before starting

# Perform model download
download_model()

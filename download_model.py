import os
import shutil
from huggingface_hub import snapshot_download
import traceback

# Check trigger
if os.environ.get("RUN_SYNC_TRIGGERED", "false").lower() != "true":
    print("[INFO] RUN_SYNC_TRIGGERED is not true. Exiting.")
    exit(0)

# Set Hugging Face token and cache directory
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set.")

os.environ["HF_HOME"] = "/runpod-volume/hf-cache"

# Define model and target path
MODEL_NAME = "stabilityai/stable-diffusion-3.5-large"
TARGET_DIR = "/runpod-volume/stable-diffusion"

# Clean existing model directory
if os.path.exists(TARGET_DIR):
    print(f"[INFO] Cleaning existing directory: {TARGET_DIR}")
    try:
        shutil.rmtree(TARGET_DIR)
        print("[INFO] Existing model directory removed.")
    except Exception as e:
        print(f"[ERROR] Failed to clean model directory: {e}")
        traceback.print_exc()
        exit(1)

# Create fresh target directory
os.makedirs(TARGET_DIR, exist_ok=True)

# Download model using symlinks to save space
try:
    print("[INFO] Downloading model...")
    snapshot_download(
        repo_id=MODEL_NAME,
        cache_dir="/runpod-volume/hf-cache",
        local_dir=TARGET_DIR,
        local_dir_use_symlinks=True,
        token=hf_token
    )
    print("[SUCCESS] Model downloaded to:", TARGET_DIR)
except Exception as e:
    print("[ERROR] Model download failed:")
    traceback.print_exc()
    exit(1)

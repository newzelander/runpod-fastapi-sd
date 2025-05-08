import os
import shutil
import subprocess
import torch
from huggingface_hub import snapshot_download, login
from diffusers import StableDiffusion3Pipeline

# --- Configuration ---
MODEL_NAME = "stabilityai/stable-diffusion-3.5-large"
PERSISTENT_VOLUME_DIR = "/runpod-volume"
CUSTOM_CACHE_DIR = os.path.join(PERSISTENT_VOLUME_DIR, "my-model-cache")
HF_TOKEN = os.getenv("HF_TOKEN")  # Set in RunPod environment variables
MODEL_DIR = os.path.join(CUSTOM_CACHE_DIR, MODEL_NAME.replace("/", "_"))

# --- Optional: Clear default Hugging Face cache (uncomment if needed) ---
# default_hf_cache = os.path.expanduser("~/.cache/huggingface")
# if os.path.exists(default_hf_cache):
#     print(f"Clearing default Hugging Face cache at {default_hf_cache}...")
#     shutil.rmtree(default_hf_cache)

# --- Persistent Volume Management ---
def clear_persistent_volume():
    """Clear all files in persistent volume to ensure there is enough space."""
    print("Clearing persistent volume...")
    for item in os.listdir(PERSISTENT_VOLUME_DIR):
        item_path = os.path.join(PERSISTENT_VOLUME_DIR, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        except Exception as e:
            print(f"Error removing {item_path}: {e}")

def check_disk_space(required_gb=15):
    """Check if there is enough free disk space on the persistent volume."""
    total, used, free = shutil.disk_usage(PERSISTENT_VOLUME_DIR)
    free_gb = free / (2**30)
    print(f"Free space in /runpod-volume: {free_gb:.2f} GB")
    return free_gb > required_gb

def get_directory_size(directory):
    """Calculate the total size of the directory (including all subdirectories)."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    return total_size

def show_disk_usage():
    """Display disk usage of the volume only."""
    print("\n=== Disk Usage for /runpod-volume ===")
    result = subprocess.run(["df", "-h", "/runpod-volume"], stdout=subprocess.PIPE, text=True)
    print(result.stdout)

def download_model():
    """Download the model from Hugging Face into custom cache."""
    if HF_TOKEN:
        login(token=HF_TOKEN)
    print("Downloading model...")
    model_path = snapshot_download(
        repo_id=MODEL_NAME,
        cache_dir=CUSTOM_CACHE_DIR,
        local_files_only=False,
        resume_download=True
    )
    
    # Report model size
    model_size = get_directory_size(MODEL_DIR)
    print(f"✅ Model downloaded. Size: {model_size / (2**30):.2f} GB")
    print(f"📁 Model cached at: {MODEL_DIR}")
    
    # List model files
    print("📦 Model files:")
    for dirpath, dirnames, filenames in os.walk(MODEL_DIR):
        for filename in filenames:
            print(f"  - {os.path.join(dirpath, filename)}")
    
    show_disk_usage()
    return model_path

def preload():
    """Ensure model is downloaded and loaded into memory."""
    if not os.path.exists(MODEL_DIR):
        if not check_disk_space():
            clear_persistent_volume()
        download_model()
    else:
        print("✅ Model already cached.")
    
    # Load model into memory
    pipe = StableDiffusion3Pipeline.from_pretrained(
        MODEL_DIR,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        use_safetensors=True
    )
    pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    return pipe

# === Load model globally ===
pipe = preload()

# === Handler for RunPod serverless ===
def preload_status(job):
    return {"status": "Model is preloaded and ready."}

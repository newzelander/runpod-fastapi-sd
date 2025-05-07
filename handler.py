import os
import shutil
import torch
from huggingface_hub import snapshot_download, login
from diffusers import StableDiffusion3Pipeline

# --- Configuration ---
MODEL_NAME = "stabilityai/stable-diffusion-3.5-large"
PERSISTENT_VOLUME_DIR = "/runpod-volume"
HF_TOKEN = os.getenv("HF_TOKEN")  # Set in RunPod environment variables
MODEL_DIR = os.path.join(PERSISTENT_VOLUME_DIR, MODEL_NAME.replace("/", "_"))

# --- Persistent Volume Management ---
def clear_persistent_volume():
    """Clear all files in persistent volume to ensure there is enough space."""
    for item in os.listdir(PERSISTENT_VOLUME_DIR):
        item_path = os.path.join(PERSISTENT_VOLUME_DIR, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

def check_disk_space(required_gb=15):
    """Check if there is enough free disk space on the persistent volume."""
    total, used, free = shutil.disk_usage(PERSISTENT_VOLUME_DIR)
    free_gb = free / (2**30)
    print(f"Free space: {free_gb:.2f} GB")
    return free_gb > required_gb

def get_directory_size(directory):
    """Calculate the total size of the directory (including all subdirectories)."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

def download_model():
    """Download the model from Hugging Face if it's not already cached."""
    if HF_TOKEN:
        login(token=HF_TOKEN)
    print("Downloading model...")
    model_path = snapshot_download(
        repo_id=MODEL_NAME,
        cache_dir=PERSISTENT_VOLUME_DIR,
        local_files_only=False
    )
    
    # Report the disk space used by the model after download
    model_size = get_directory_size(MODEL_DIR)
    print(f"Model downloaded. The size of the model is approximately {model_size / (2**30):.2f} GB")
    
    # Show where the model is cached
    print(f"Model is cached at: {MODEL_DIR}")
    print("Directories where model is saved:")
    for dirpath, dirnames, filenames in os.walk(MODEL_DIR):
        print(f"Found directory: {dirpath}")
        for filename in filenames:
            print(f"  File: {os.path.join(dirpath, filename)}")
    
    return model_path

def preload():
    """Ensure the model is preloaded into memory, checking if it already exists in cache."""
    if not os.path.exists(MODEL_DIR):
        if not check_disk_space():
            clear_persistent_volume()
        # If model isn't cached, download it
        download_model()
    else:
        print("Model already cached, skipping download.")
    
    # Load model from cache
    pipe = StableDiffusion3Pipeline.from_pretrained(
        MODEL_DIR,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        use_safetensors=True
    )
    pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    return pipe

# Load model once per container session
pipe = preload()

# RunPod Serverless Handler (without image generation for now)
def preload_status(job):
    """Return the current status of the model preload process."""
    return {"status": "Model is preloaded and ready for future use."}

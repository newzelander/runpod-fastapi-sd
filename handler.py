import os
import shutil
from diffusers import StableDiffusion3Pipeline
import torch
import runpod

# Persistent paths
VOLUME_PATH = "/runpod-volume"
MODEL_DIR = os.path.join(VOLUME_PATH, "models")
CACHE_DIR = os.path.join(VOLUME_PATH, "cache")
MODEL_NAME = "stabilityai/stable-diffusion-3.5-large"
MODEL_PATH = os.path.join(MODEL_DIR, "stable-diffusion-3.5-large")

# ✅ Redirect Hugging Face cache to persistent volume
os.environ["HF_HOME"] = CACHE_DIR

def remove_all(path):
    """Recursively delete all files and directories in the given path."""
    if os.path.exists(path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Error deleting {item_path}: {e}")

def get_dir_size(path):
    """Get the total size of a directory in bytes."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

def list_directory_contents(path):
    """List all files and directories in a given path."""
    if os.path.exists(path):
        print(f"\nContents of {path}:")
        for root, dirs, files in os.walk(path):
            for name in dirs:
                print(f"Directory: {os.path.join(root, name)}")
            for name in files:
                print(f"File: {os.path.join(root, name)}")

def download_model():
    """Download the model directly into cache, then move to model path."""
    os.makedirs(MODEL_PATH, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(os.path.join(MODEL_PATH, "model_index.json")):
        print("✅ Model already exists.")
    else:
        try:
            print("⬇️ Downloading model to cache folder...")
            # Download the model into the cache directory
            pipe = StableDiffusion3Pipeline.from_pretrained(
                pretrained_model_name_or_path=MODEL_NAME,
                torch_dtype=torch.float16,
                use_safetensors=True,
                variant="fp16",
                cache_dir=CACHE_DIR  # Download model into the cache folder
            )
            
            # Move the downloaded model to the model path
            print(f"✅ Moving model from {CACHE_DIR} to {MODEL_PATH}...")
            shutil.move(CACHE_DIR, MODEL_PATH)
            print("✅ Model moved to model path.")

            # Optionally clean the cache after moving
            remove_all(CACHE_DIR)
            print("✅ Cache cleaned.")

        except Exception as e:
            print(f"❌ Error during model download and move: {e}")
            return None

    return pipe

def display_storage_info():
    """Display the contents and sizes of the model and cache directories."""
    print("\n### Directory Information ###")
    
    # Display contents and sizes of directories
    list_directory_contents(MODEL_PATH)
    model_size = get_dir_size(MODEL_PATH)
    print(f"\nTotal size of {MODEL_PATH}: {model_size / (1024 * 1024):.2f} MB")

    list_directory_contents(CACHE_DIR)
    cache_size = get_dir_size(CACHE_DIR)
    print(f"\nTotal size of {CACHE_DIR}: {cache_size / (1024 * 1024):.2f} MB")

def handler(job):
    input_data = job.get("input", {})
    if input_data.get("action") == "clean":
        print("💻 Cleaning model and cache folders...")
        remove_all(MODEL_PATH)
        pipe = download_model()

        if pipe is not None:
            display_storage_info()
            return {
                "status": "success",
                "message": "Model downloaded and moved to model path."
            }
        else:
            return {
                "status": "failure",
                "message": "An error occurred during the model download process."
            }
    else:
        print("❌ No valid action provided. Skipping.")
        return {"status": "skipped", "reason": "No valid action provided."}

# RunPod serverless start
runpod.serverless.start({"handler": handler})

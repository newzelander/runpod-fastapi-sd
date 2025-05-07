import os
import shutil
from diffusers import StableDiffusion3Pipeline  # Corrected pipeline import
import runpod

VOLUME_PATH = "/runpod-volume"
HF_CACHE_DIR = VOLUME_PATH  # Set cache directory to the volume

def remove_all(path):
    """Recursively delete all files and directories in the given path."""
    if os.path.exists(path):
        print(f"Deleting contents of: {path}")
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Error deleting {item_path}: {e}")
    else:
        print(f"{path} does not exist.")

def cleanup_phase():
    """Clear all volumes and caches."""
    # Clean /runpod-volume
    remove_all(VOLUME_PATH)

    # Clean Hugging Face cache
    hf_cache = os.path.expanduser("~/.cache/huggingface")
    if os.path.exists(hf_cache):
        print("Deleting Hugging Face cache...")
        shutil.rmtree(hf_cache)

    print("✅ Cleanup complete.")

def download_model():
    """Download and load the model using from_pretrained."""
    # Prevent Hugging Face from using internal cache
    os.environ["HF_HUB_DISABLE_CACHE"] = "1"
    
    # Explicitly set the cache directory to avoid temporary files
    print(f"Downloading model to {HF_CACHE_DIR}")
    
    repo_id = "stabilityai/stable-diffusion-3.5-large"
    pipe = StableDiffusion3Pipeline.from_pretrained(repo_id, cache_dir=HF_CACHE_DIR)
    
    print("✅ Model download and load complete.")
    return pipe

def handler(job):
    input_data = job.get("input", {})
    
    if input_data.get("action") == "clean":
        cleanup_phase()
        pipe = download_model()  # This will download and load the model
        return {"status": "success", "message": "Model downloaded and loaded."}
    else:
        return {"status": "skipped", "reason": "No valid action provided."}

# Register the handler function with RunPod
runpod.serverless.start({"handler": handler})

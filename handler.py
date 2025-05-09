import os
import shutil
from diffusers import StableDiffusion3Pipeline
import runpod

VOLUME_PATH = "/runpod-volume"
HF_CACHE_DIR = os.path.join(VOLUME_PATH, "cache")     # Cache goes here
MODEL_DIR = os.path.join(VOLUME_PATH, "models")       # Models go here
MODEL_NAME = "stable-diffusion-3.5-large"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

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
    remove_all(VOLUME_PATH)

    # Also clear default Hugging Face user cache just in case
    hf_cache = os.path.expanduser("~/.cache/huggingface")
    if os.path.exists(hf_cache):
        print("Deleting Hugging Face cache...")
        shutil.rmtree(hf_cache)

    print("✅ Cleanup complete.")

def download_model():
    """Download and load the model using from_pretrained."""
    print(f"Downloading model to: {MODEL_PATH}")
    print(f"Using cache directory: {HF_CACHE_DIR}")

    # Set custom cache directory
    os.environ["HF_HOME"] = HF_CACHE_DIR  # This sets the base for all HF caching

    # Ensure directories exist
    os.makedirs(HF_CACHE_DIR, exist_ok=True)
    os.makedirs(MODEL_PATH, exist_ok=True)

    try:
        # Download directly to MODEL_PATH, using HF_CACHE_DIR for any temp use
        pipe = StableDiffusion3Pipeline.from_pretrained(
            pretrained_model_name_or_path=MODEL_NAME,
            cache_dir=HF_CACHE_DIR,
            local_files_only=False,  # Only specify this once
            variant=None,
            torch_dtype=None,
            use_safetensors=True,
            resume_download=True,
            force_download=False,
            ignore_mismatched_sizes=False,
            revision=None
        )
        print("✅ Model download and load complete.")
        
        # After the model is downloaded, list the files and calculate the total size
        list_files_and_size(MODEL_PATH)
        list_cache_size(HF_CACHE_DIR)
        
        return pipe
    except Exception as e:
        print(f"Error downloading model: {e}")
        return None

def list_files_and_size(path):
    """List all files in the directory and calculate total size."""
    total_size = 0
    print("\nListing files and directories in model path:")
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subtotal = 0
        for f in files:
            file_path = os.path.join(root, f)
            file_size = os.path.getsize(file_path)
            subtotal += file_size
            print(f"{indent}    {f} - {file_size / (1024 * 1024):.2f} MB")
        total_size += subtotal
        if subtotal > 0:
            print(f"{indent}    Total size of this folder: {subtotal / (1024 * 1024):.2f} MB")
    
    print(f"\nTotal size of model files: {total_size / (1024 * 1024):.2f} MB\n")

def list_cache_size(path):
    """Calculate and display the total size of the cache directory."""
    total_size = 0
    print("\nCalculating size of cache directory:")
    for root, dirs, files in os.walk(path):
        for f in files:
            file_path = os.path.join(root, f)
            total_size += os.path.getsize(file_path)
    
    print(f"Total size of cache directory: {total_size / (1024 * 1024):.2f} MB\n")

def handler(job):
    input_data = job.get("input", {})
    
    if input_data.get("action") == "clean":
        cleanup_phase()
        pipe = download_model()
        if pipe:
            return {"status": "success", "message": "Model downloaded and loaded."}
        else:
            return {"status": "error", "message": "Model download failed."}
    else:
        return {"status": "skipped", "reason": "No valid action provided."}

# Register handler with RunPod
runpod.serverless.start({"handler": handler})

import os
import shutil
from huggingface_hub import hf_hub_download, list_repo_files
import runpod

VOLUME_PATH = "/runpod-volume"

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

def download_phase():
    """Download model to the clean volume."""
    # Prevent HF from using internal cache
    os.environ["HF_HUB_DISABLE_CACHE"] = "1"

    # Define the model repository
    repo_id = "stabilityai/stable-diffusion-3.5-large"
    
    # List all available files in the repository
    repo_files = list_repo_files(repo_id)
    
    # Download each file
    for filename in repo_files:
        try:
            hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=VOLUME_PATH,
                force_download=True
            )
            print(f"✅ Downloaded: {filename}")
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
    
    print("✅ Model download complete.")

def run_cleanup(job):
    input_data = job["input"]
    if input_data.get("action") == "clean":
        cleanup_phase()
        download_phase()
        return {"status": "success"}
    else:
        return {"status": "skipped", "reason": "No valid action provided."}

# Register the function with RunPod
runpod.serverless.start({"handler": run_cleanup})

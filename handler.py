import os
import shutil
from huggingface_hub import list_repo_files, hf_hub_download
import runpod

# Path for the volume where the model files will be stored
VOLUME_PATH = "/runpod-volume"

# Function to delete all files and directories in a given path
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

# Function to clear out the volume and Hugging Face cache
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

# Function to dynamically download all files from Hugging Face repository
def download_model():
    """Download model to the clean volume."""
    # Prevent Hugging Face from using internal cache
    os.environ["HF_HUB_DISABLE_CACHE"] = "1"

    # Define the model repository ID
    repo_id = "stabilityai/stable-diffusion-3.5-large"
    
    # List all files in the model repository
    files = list_repo_files(repo_id)

    # Download each file from the repository
    for file in files:
        print(f"Downloading: {file}")
        hf_hub_download(
            repo_id=repo_id,
            filename=file,
            local_dir=VOLUME_PATH,
            force_download=True
        )

    print("✅ Model download complete.")

# Main handler function for RunPod serverless
def handler(job):
    input_data = job.get("input", {})
    
    # Check if the action is 'clean', then perform cleanup and download
    if input_data.get("action") == "clean":
        cleanup_phase()
        download_model()
        return {"status": "success"}
    else:
        return {"status": "skipped", "reason": "No valid action provided."}

# Register the handler function with RunPod
runpod.serverless.start({"handler": handler})

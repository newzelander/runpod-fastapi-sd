import os
import shutil
import subprocess
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

def get_disk_usage():
    """Get the disk usage of the persistent volume."""
    try:
        output = subprocess.check_output(['df', '-h', VOLUME_PATH]).decode('utf-8')
        lines = output.splitlines()
        # Extract the line containing the disk usage information
        disk_info = lines[1].split()
        total = disk_info[1]
        used = disk_info[2]
        available = disk_info[3]
        return {
            "total": total,
            "used": used,
            "available": available
        }
    except subprocess.CalledProcessError as e:
        print(f"Error getting disk usage: {e}")
        return None

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

    # Download model into /runpod-volume
    snapshot_download(
        repo_id="stabilityai/stable-diffusion-3.5-large",
        local_dir=VOLUME_PATH,
        local_dir_use_symlinks=False,
        resume_download=False  # Full clean download
    )

    print("✅ Model download complete.")

def run_cleanup(job):
    input_data = job["input"]
    if input_data.get("action") == "clean":
        # Get disk usage before cleanup
        disk_usage_before_cleanup = get_disk_usage()

        cleanup_phase()

        # Get disk usage after cleanup
        disk_usage_after_cleanup = get_disk_usage()

        # Run the model download phase
        download_phase()

        # Get disk usage after download
        disk_usage_after_download = get_disk_usage()

        return {
            "status": "success",
            "disk_usage_before_cleanup": disk_usage_before_cleanup,
            "disk_usage_after_cleanup": disk_usage_after_cleanup,
            "disk_usage_after_download": disk_usage_after_download
        }
    else:
        return {"status": "skipped", "reason": "No valid action provided."}

# Register the function with RunPod
runpod.serverless.start({"handler": run_cleanup})

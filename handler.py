import os
import shutil
from huggingface_hub import snapshot_download, login
import runpod

# Get disk usage for the /runpod-volume (in GB)
def get_volume_disk_usage(path="/runpod-volume"):
    total, used, free = shutil.disk_usage(path)
    return {
        "total_gb": round(total / (1024 ** 3), 2),  # Convert bytes to GB
        "used_gb": round(used / (1024 ** 3), 2),
        "free_gb": round(free / (1024 ** 3), 2)
    }

# Clear /runpod-volume
def clear_runpod_volume():
    folder = "/runpod-volume"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def handler(event, context):
    print(f"Event: {event}")
    print(f"Context: {context}")

    inputs = event.get("input", {})
    model_name = inputs.get("model")
    cache_dir = inputs.get("cache_directory", "/runpod-volume/huggingface-cache")
    max_disk_usage = float(inputs.get("max_disk_usage", 0.9))
    check_disk_space = inputs.get("check_disk_space", True)

    if not model_name:
        return {"error": "Missing 'model' in input."}

    print("Clearing /runpod-volume...")
    clear_runpod_volume()

    if check_disk_space:
        usage_before = get_volume_disk_usage()
        print(f"Disk usage before download (for /runpod-volume): {usage_before}")
        
        if (shutil.disk_usage("/runpod-volume").used /
                shutil.disk_usage("/runpod-volume").total) > max_disk_usage:
            return {"error": "Disk usage exceeds limit before download. Volume has been cleared."}

    try:
        print("Logging in to Hugging Face...")
        login(token=os.environ.get("HF_TOKEN"))

        print(f"Downloading model: {model_name}")
        model_path = snapshot_download(
            repo_id=model_name,
            cache_dir=cache_dir,
            local_files_only=False,
            force_download=True  # Ensure no duplication
        )

        # Check disk usage after download
        usage_after = get_volume_disk_usage()
        print(f"Disk usage after download (for /runpod-volume): {usage_after}")

        return {
            "status": "Download complete",
            "model_path": model_path,
            "disk_usage_before": usage_before,
            "disk_usage_after": usage_after
        }

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {"error": str(e)}

# Ensure serverless worker is started
runpod.serverless.start({"handler": handler})

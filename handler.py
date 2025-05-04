import os
import shutil
from huggingface_hub import snapshot_download, login
import runpod

# Helper to get disk usage stats for /runpod-volume
def get_volume_disk_usage(path="/runpod-volume"):
    total, used, free = shutil.disk_usage(path)
    return {
        "total_gb": round(total / (1024 ** 3), 2),
        "used_gb": round(used / (1024 ** 3), 2),
        "free_gb": round(free / (1024 ** 3), 2)
    }

# Safely clear the contents of /runpod-volume without removing the mount point
def clear_runpod_volume():
    folder = "/runpod-volume"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # remove file or link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # remove directory
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

# ❗ FIXED: Remove context — only accept one argument
def handler(event):
    print(f"Event: {event}")
    
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
        usage = shutil.disk_usage("/runpod-volume")
        if usage.used / usage.total > max_disk_usage:
            return {"error": "Disk usage exceeds limit before download. Volume has been cleared."}

    try:
        print("Logging in to Hugging Face...")
        login(token=os.environ.get("HF_TOKEN"))

        print(f"Downloading model: {model_name}")
        model_path = snapshot_download(
            repo_id=model_name,
            cache_dir=cache_dir,
            local_files_only=False,
            resume_download=True
        )

        disk_usage = get_volume_disk_usage()

        return {
            "status": "Download complete",
            "model_path": model_path,
            "disk_usage": disk_usage
        }

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {"error": str(e)}

# ✅ Required for serverless
runpod.serverless.start({"handler": handler})

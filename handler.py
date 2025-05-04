import os
import shutil
from huggingface_hub import snapshot_download, login
import runpod

def get_volume_disk_usage(path="/runpod-volume"):
    total, used, free = shutil.disk_usage(path)
    return {
        "total_gb": round(total / (1024 ** 3), 2),
        "used_gb": round(used / (1024 ** 3), 2),
        "free_gb": round(free / (1024 ** 3), 2)
    }

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
    print("Handler invoked")
    
    # Extract input parameters from the event
    inputs = event.get("input", {})
    model_name = inputs.get("model")
    cache_dir = inputs.get("cache_directory", "/runpod-volume/huggingface-cache")
    max_disk_usage = float(inputs.get("max_disk_usage", 0.9))
    check_disk_space = inputs.get("check_disk_space", True)

    # Ensure model name is provided in the event
    if not model_name:
        return {"error": "Missing 'model' in input."}

    print("Clearing /runpod-volume...")
    clear_runpod_volume()

    # Check disk space before downloading
    if check_disk_space:
        usage = shutil.disk_usage("/runpod-volume")
        if usage.used / usage.total > max_disk_usage:
            return {"error": "Disk usage exceeds limit before download. Volume has been cleared."}

    try:
        print("Logging in to Hugging Face...")
        # Login to Hugging Face with the provided token
        login(token=os.environ.get("HF_TOKEN"))

        print(f"Downloading model: {model_name}")
        # Download the model from Hugging Face
        model_path = snapshot_download(
            repo_id=model_name,
            cache_dir=cache_dir,
            local_files_only=False,
            resume_download=True
        )

        print(f"Model downloaded successfully to: {model_path}")

        # After download, report how much space is used
        disk_usage = get_volume_disk_usage()

        return {
            "status": "Download complete",
            "model_path": model_path,
            "disk_usage": disk_usage
        }

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {"error": str(e)}

# Ensure you start the serverless function with both event and context parameters.
runpod.serverless.start({
    "handler": handler
})

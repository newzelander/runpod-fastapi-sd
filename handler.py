import os
import shutil
import subprocess
from runpod.serverless.modules.rp_handler import RunPodHandler
from huggingface_hub import snapshot_download, login
import shutil

# Helper to get disk usage stats for /runpod-volume
def get_volume_disk_usage(path="/runpod-volume"):
    total, used, free = shutil.disk_usage(path)
    return {
        "total_gb": round(total / (1024 ** 3), 2),
        "used_gb": round(used / (1024 ** 3), 2),
        "free_gb": round(free / (1024 ** 3), 2)
    }

def handler(event):
    inputs = event.get("input", {})
    model_name = inputs.get("model")
    cache_dir = inputs.get("cache_directory", "/runpod-volume/huggingface-cache")
    max_disk_usage = float(inputs.get("max_disk_usage", 0.9))
    check_disk_space = inputs.get("check_disk_space", True)

    if not model_name:
        return {"error": "Missing 'model' in input."}

    # Clean up the persistent volume
    if os.path.exists("/runpod-volume"):
        shutil.rmtree("/runpod-volume")
        os.makedirs("/runpod-volume")

    # Check disk space before downloading
    if check_disk_space:
        usage = shutil.disk_usage("/runpod-volume")
        if usage.used / usage.total > max_disk_usage:
            return {"error": "Disk usage exceeds limit before download. Volume has been cleared."}

    try:
        login(token=os.environ.get("HF_TOKEN"))

        model_path = snapshot_download(
            repo_id=model_name,
            cache_dir=cache_dir,
            local_files_only=False,
            resume_download=True
        )

        # After download, report how much space is used
        disk_usage = get_volume_disk_usage()

        return {
            "status": "Download complete",
            "model_path": model_path,
            "disk_usage": disk_usage
        }

    except Exception as e:
        return {"error": str(e)}

# Register handler
handler = RunPodHandler(handler)

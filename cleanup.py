import os
import shutil
import runpod

VOLUME_PATH = "/runpod-volume"

def remove_all(path):
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
    total, used, free = shutil.disk_usage(VOLUME_PATH)
    return {
        "total_gb": round(total / (1024**3), 2),
        "used_gb": round(used / (1024**3), 2),
        "free_gb": round(free / (1024**3), 2)
    }

def run_cleanup(job):
    input_data = job["input"]
    if input_data.get("action") == "clean":
        remove_all(VOLUME_PATH)

        # Delete Hugging Face cache
        hf_cache = os.path.expanduser("~/.cache/huggingface")
        if os.path.exists(hf_cache):
            print("Deleting Hugging Face cache...")
            shutil.rmtree(hf_cache)

        print("✅ Cleanup complete.")
        return {
            "status": "success",
            "disk_usage_after_cleanup": get_disk_usage()
        }
    else:
        return {"status": "skipped", "reason": "No valid action provided."}

# Register the function with RunPod
runpod.serverless.start({"handler": run_cleanup})

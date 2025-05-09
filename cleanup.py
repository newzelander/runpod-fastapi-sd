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
    """Accurately get the disk usage of /runpod-volume using du."""
    try:
        output = subprocess.check_output(['du', '-sh', VOLUME_PATH]).decode('utf-8')
        size, _ = output.split("\t")
        return {
            "used_by_runpod_volume": size
        }
    except subprocess.CalledProcessError as e:
        print(f"Error getting disk usage: {e}")
        return None

def cleanup_phase():
    """Clear /runpod-volume and Hugging Face cache."""
    remove_all(VOLUME_PATH)

    hf_cache = os.path.expanduser("~/.cache/huggingface")
    if os.path.exists(hf_cache):
        print("Deleting Hugging Face cache...")
        shutil.rmtree(hf_cache)

    print("✅ Cleanup complete.")

def run_cleanup(job):
    input_data = job["input"]
    if input_data.get("action") == "clean":
        usage_before = get_disk_usage()

        cleanup_phase()

        usage_after = get_disk_usage()

        return {
            "status": "success",
            "disk_usage_before_cleanup": usage_before,
            "disk_usage_after_cleanup": usage_after
        }
    else:
        return {"status": "skipped", "reason": "No valid action provided."}

runpod.serverless.start({"handler": run_cleanup})

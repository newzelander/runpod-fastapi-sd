import os
import shutil
import sys
import json
import psutil  # This will allow us to check disk usage

# Function to get disk usage in a human-readable format
def get_disk_usage(path):
    usage = psutil.disk_usage(path)
    return f"Total: {usage.total / (1024 ** 3):.2f} GB, Used: {usage.used / (1024 ** 3):.2f} GB, Free: {usage.free / (1024 ** 3):.2f} GB"

# Reading input from Runpod job (passed as JSON)
input_data = json.loads(sys.argv[1])  # The first argument should be the JSON input

action = input_data.get('input', {}).get('action', None)

# Only proceed with cleanup if action is 'clean'
if action == 'clean':
    VOLUME_PATH = "/runpod-volume"

    # Show disk space before cleanup
    print(f"Disk space before cleanup: {get_disk_usage(VOLUME_PATH)}")

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

    # Delete everything in /runpod-volume
    remove_all(VOLUME_PATH)

    # Also delete Hugging Face cache
    hf_cache = os.path.expanduser("~/.cache/huggingface")
    if os.path.exists(hf_cache):
        print("Deleting Hugging Face cache...")
        shutil.rmtree(hf_cache)

    print("✅ Cleanup complete.")

    # Show disk space after cleanup
    print(f"Disk space after cleanup: {get_disk_usage(VOLUME_PATH)}")

else:
    print("No valid action specified. Skipping cleanup.")

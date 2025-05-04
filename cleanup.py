import os
import shutil

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

# Delete everything in /runpod-volume
remove_all(VOLUME_PATH)

# Also delete Hugging Face cache
hf_cache = os.path.expanduser("~/.cache/huggingface")
if os.path.exists(hf_cache):
    print("Deleting Hugging Face cache...")
    shutil.rmtree(hf_cache)

print("✅ Cleanup complete.")

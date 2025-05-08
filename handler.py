import os
import shutil
import subprocess
from huggingface_hub import snapshot_download
import runpod

# Show existing folders and paths
def show_existing_paths():
    print("\n📁 Existing folders and paths:")
    paths_to_check = [
        "/runpod-volume",
        os.path.expanduser("~/.cache/huggingface/hub")
    ]
    for path in paths_to_check:
        print(f"✅ Found: {path}" if os.path.exists(path) else f"❌ Not found: {path}")

# Clear directory contents
def clear_directory_contents():
    print("\n🧹 Clearing directory contents...")
    paths_to_clear = [
        "/runpod-volume",
        os.path.expanduser("~/.cache/huggingface/hub")
    ]
    for path in paths_to_clear:
        if os.path.exists(path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                except Exception as e:
                    print(f"⚠️ Failed to delete {item_path}: {e}")
            print(f"✅ Cleared: {path}")
        else:
            print(f"ℹ️ Path does not exist: {path}")

# Show all files and directories in the given path
def list_files_in_directory(path):
    print(f"\n📂 Listing all files and directories in {path}:")
    for root, dirs, files in os.walk(path):
        for name in files:
            print(f"File: {os.path.join(root, name)}")
        for name in dirs:
            print(f"Directory: {os.path.join(root, name)}")

# Set Hugging Face cache location
def configure_hugging_face_cache():
    print("\n⚙️ Configuring Hugging Face cache...")
    os.environ["HF_HUB_CACHE"] = "/runpod-volume"

# Show available disk space on /runpod-volume
def show_available_disk_space():
    statvfs = os.statvfs("/runpod-volume")
    free_bytes = statvfs.f_frsize * statvfs.f_bavail
    free_gb = free_bytes / (1024 ** 3)
    print(f"\n🧮 Available disk space: {free_gb:.2f} GB on /runpod-volume")

# Load the model
def preload_model():
    print("\n🚀 Preloading model...")

    model_dir = "/runpod-volume"

    if not os.path.exists(os.path.join(model_dir, "model_index.json")):
        print("📦 Model not found locally. Downloading...")
        try:
            snapshot_download(
                repo_id="stabilityai/stable-diffusion-3.5-large",  # Correct model path
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
            print("✅ Model downloaded to:", model_dir)
        except Exception as e:
            return {"status": "error", "message": f"Download failed: {e}"}
    else:
        print("📁 Model already exists at:", model_dir)

    show_available_disk_space()
    list_files_in_directory(model_dir)  # Show all files and directories

    return {"status": "success", "message": "Model downloaded."}

# RunPod handler
def handler(event):
    print("\n📥 Received event:", event)
    action = event.get("input", {}).get("action", "")

    if action == "preload_model":
        show_existing_paths()
        clear_directory_contents()
        configure_hugging_face_cache()
        return preload_model()
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}

# Start RunPod serverless job handler
runpod.serverless.start({"handler": handler})

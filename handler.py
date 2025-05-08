import os
import shutil
import subprocess
from huggingface_hub import snapshot_download
import runpod

# ----------------------------- #
# ✅ Set Hugging Face cache path
# ----------------------------- #
os.environ["HF_HOME"] = "/runpod-volume"
os.environ["HF_HUB_CACHE"] = "/runpod-volume"
os.environ["TRANSFORMERS_CACHE"] = "/runpod-volume"  # optional, good practice

# ----------------------------- #
# 🧹 Clean old Hugging Face cache (if exists)
# ----------------------------- #
def clean_default_huggingface_cache():
    default_path = "/root/.cache/huggingface"
    if os.path.exists(default_path):
        print(f"🧹 Removing default Hugging Face cache at {default_path}...")
        shutil.rmtree(default_path, ignore_errors=True)
        print("✅ Removed.")

# ----------------------------- #
# 📁 Show folder structure
# ----------------------------- #
def show_directory_tree(path, prefix=""):
    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        print(f"{prefix}📁 {item}" if os.path.isdir(item_path) else f"{prefix}📄 {item}")
        if os.path.isdir(item_path):
            show_directory_tree(item_path, prefix + "    ")

# ----------------------------- #
# 📊 Show disk usage for /runpod-volume
# ----------------------------- #
def show_disk_usage():
    try:
        output = subprocess.check_output(['du', '-sh', '/runpod-volume']).decode('utf-8')
        size = output.split()[0]
        print(f"\n💾 Disk usage: {size}B on /runpod-volume")
    except Exception as e:
        print(f"❌ Error checking disk usage: {e}")

# ----------------------------- #
# 🚀 Preload model
# ----------------------------- #
def preload_model():
    print("\n🚀 Starting model download...")

    model_dir = "/runpod-volume"
    model_index_path = os.path.join(model_dir, "model_index.json")

    if not os.path.exists(model_index_path):
        print("📦 Model not found locally. Downloading...")
        try:
            snapshot_download(
                repo_id="stabilityai/stable-diffusion-3.5-large",
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
            print("✅ Model downloaded to:", model_dir)
        except Exception as e:
            return {"status": "error", "message": f"Download failed: {e}"}
    else:
        print("📁 Model already exists at:", model_dir)

    # Show results
    show_disk_usage()
    print("\n📂 Directory structure in /runpod-volume:")
    show_directory_tree("/runpod-volume")

    return {"status": "success", "message": "Model is available on /runpod-volume."}

# ----------------------------- #
# 🔧 RunPod handler
# ----------------------------- #
def handler(event):
    print("\n📥 Received event:", event)
    action = event.get("input", {}).get("action", "")

    if action == "preload_model":
        clean_default_huggingface_cache()
        return preload_model()
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}

# ----------------------------- #
# 🔌 Start RunPod serverless job
# ----------------------------- #
runpod.serverless.start({"handler": handler})

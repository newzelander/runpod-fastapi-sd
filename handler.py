import os
import shutil
import subprocess
from huggingface_hub import hf_hub_download
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
# 🧹 Delete everything in /runpod-volume
# ----------------------------- #
def clean_runpod_volume():
    runpod_volume_path = "/runpod-volume"
    if os.path.exists(runpod_volume_path):
        print(f"🧹 Deleting everything in {runpod_volume_path}...")
        shutil.rmtree(runpod_volume_path)
        os.makedirs(runpod_volume_path)  # Recreate the directory
        print(f"✅ Deleted everything in {runpod_volume_path} and recreated the directory.")
    else:
        print(f"❌ {runpod_volume_path} does not exist.")

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
# 🚀 Preload model with minimal files
# ----------------------------- #
def preload_model():
    print("\n🚀 Starting selective model file download...")

    repo_id = "stabilityai/stable-diffusion-3.5-large"
    model_dir = "/runpod-volume/stabilityai/stable-diffusion-3.5-large"  # Updated path

    # Create the model directory if it doesn't exist
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        print(f"📂 Created model directory at {model_dir}")

    files_to_download = [
        "model_index.json",
        "config.json",
        "scheduler/scheduler_config.json",
        "tokenizer/merges.txt",
        "tokenizer/vocab.json",
        "tokenizer/tokenizer.json",
        "text_encoder/config.json",
        "text_encoder/model.safetensors",
        "unet/diffusion_pytorch_model.safetensors",
        "vae/config.json",
        "vae/diffusion_pytorch_model.safetensors"
    ]

    try:
        # Clean /runpod-volume before starting the download
        clean_runpod_volume()

        for file in files_to_download:
            print(f"⬇️  Downloading: {file}")
            hf_hub_download(
                repo_id=repo_id,
                filename=file,
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
        print("✅ All required files downloaded.")
    except Exception as e:
        return {"status": "error", "message": f"Download failed: {e}"}

    show_disk_usage()
    print("\n📂 Directory structure in /runpod-volume/stabilityai/stable-diffusion-3.5-large:")
    show_directory_tree(model_dir)

    return {"status": "success", "message": "Model is available with minimal files."}

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

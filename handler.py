import os
import shutil
import subprocess
from huggingface_hub import hf_hub_download, login
from huggingface_hub.utils import EntryNotFoundError
import runpod

# Set cache
os.environ["HF_HOME"] = "/runpod-volume/huggingface_cache"
os.environ["HF_HUB_CACHE"] = "/runpod-volume/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "/runpod-volume/huggingface_cache"

def clean_runpod_volume_contents():
    base_path = "/runpod-volume"
    print("🧹 Deleting contents inside /runpod-volume...")
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        except Exception as e:
            print(f"❌ Failed to delete {item_path}: {e}")
    print("✅ Cleaned contents of /runpod-volume.")

def check_directory_permissions(path):
    if os.access(path, os.W_OK):
        print(f"✅ {path} is writable.")
    else:
        print(f"❌ {path} is not writable or accessible.")

def show_directory_tree(path, prefix=""):
    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        print(f"{prefix}📁 {item}" if os.path.isdir(item_path) else f"{prefix}📄 {item}")
        if os.path.isdir(item_path):
            show_directory_tree(item_path, prefix + "    ")

def show_disk_usage():
    try:
        output = subprocess.check_output(['du', '-sh', '/runpod-volume']).decode('utf-8')
        size = output.split()[0]
        print(f"\n💾 Disk usage: {size}B on /runpod-volume")
    except Exception as e:
        print(f"❌ Error checking disk usage: {e}")

def preload_model():
    print("\n🚀 Starting selective model file download...")
    model_dir = "/runpod-volume/stabilityai/stable-diffusion-3.5-large"
    repo_id = "stabilityai/stable-diffusion-3.5-large"

    try:
        clean_runpod_volume_contents()

        if not os.path.exists(model_dir):
            os.makedirs(model_dir, exist_ok=True)
            print(f"📂 Created model directory at {model_dir}")

        check_directory_permissions("/runpod-volume")
        check_directory_permissions(model_dir)

        files_to_download = [
            "model_index.json",
            # Consider commenting this if it's 404-ing
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

        for file in files_to_download:
            print(f"⬇️  Downloading: {file}")
            try:
                hf_hub_download(
                    repo_id=repo_id,
                    filename=file,
                    local_dir=model_dir,
                    local_dir_use_symlinks=False
                )
                print(f"✅ Successfully downloaded: {file}")
            except EntryNotFoundError:
                print(f"❌ File not found on HuggingFace: {file}")
            except Exception as e:
                print(f"❌ Failed to download {file}: {e}")

        show_disk_usage()
        print("\n📂 Directory structure:")
        show_directory_tree(model_dir)

        return {"status": "success", "message": "Model is available with minimal files."}

    except Exception as e:
        return {"status": "error", "message": f"Download failed: {e}"}

def handler(event):
    print("\n📥 Received event:", event)
    action = event.get("input", {}).get("action", "")
    if action == "preload_model":
        return preload_model()
    else:
        return {"status": "error", "message": f"Unknown action: {action}"}

runpod.serverless.start({"handler": handler})

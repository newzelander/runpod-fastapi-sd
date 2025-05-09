import os
import shutil
from diffusers import StableDiffusion3Pipeline
import torch
import runpod

# Persistent paths
VOLUME_PATH = "/runpod-volume"
MODEL_DIR = os.path.join(VOLUME_PATH, "models")
CACHE_DIR = os.path.join(VOLUME_PATH, "cache")
MODEL_NAME = "stabilityai/stable-diffusion-3.5-large"
MODEL_PATH = os.path.join(MODEL_DIR, "stable-diffusion-3.5-large")

# ✅ Redirect Hugging Face cache to persistent volume
os.environ["HF_HOME"] = CACHE_DIR

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

def cleanup_phase():
    """Clear model and cache folders."""
    remove_all(VOLUME_PATH)

    # Extra safety: clear Hugging Face user-level cache too
    hf_user_cache = os.path.expanduser("~/.cache/huggingface")
    if os.path.exists(hf_user_cache):
        print("Deleting Hugging Face user cache...")
        shutil.rmtree(hf_user_cache)

    print("✅ Cleanup complete.")

def list_files_and_size(path, title=""):
    total_size = 0
    print(f"\n📁 Listing files in {title or path}:")
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subtotal = 0
        for f in files:
            file_path = os.path.join(root, f)
            file_size = os.path.getsize(file_path)
            subtotal += file_size
            print(f"{indent}    {f} - {file_size / (1024 * 1024):.2f} MB")
        total_size += subtotal
        if subtotal > 0:
            print(f"{indent}    Folder size: {subtotal / (1024 * 1024):.2f} MB")
    print(f"\n📦 Total size in {title or path}: {total_size / (1024 * 1024):.2f} MB\n")

def download_model():
    """Download model only into MODEL_PATH using custom cache."""
    print(f"Preparing model directory: {MODEL_PATH}")
    os.makedirs(MODEL_PATH, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(os.path.join(MODEL_PATH, "model_index.json")):
        print("✅ Model already exists in MODEL_PATH.")
    else:
        print("⬇️ Downloading model directly into MODEL_PATH...")
        pipe = StableDiffusion3Pipeline.from_pretrained(
            pretrained_model_name_or_path=MODEL_NAME,
            torch_dtype=torch.float16,
            use_safetensors=True,
            resume_download=True,
            cache_dir=CACHE_DIR
        )
        pipe.save_pretrained(MODEL_PATH)
        print("✅ Model downloaded and saved to MODEL_PATH.")

    pipe = StableDiffusion3Pipeline.from_pretrained(
        pretrained_model_name_or_path=MODEL_PATH,
        torch_dtype=torch.float16,
        use_safetensors=True
    ).to("cuda")

    print("✅ Model loaded onto GPU from MODEL_PATH.")

    list_files_and_size(MODEL_PATH, "MODEL_PATH")
    list_files_and_size(CACHE_DIR, "CACHE_DIR")

    return pipe

def handler(job):
    input_data = job.get("input", {})
    if input_data.get("action") == "clean":
        cleanup_phase()
        pipe = download_model()
        if pipe:
            return {"status": "success", "message": "Model downloaded, loaded, and cache inspected."}
        else:
            return {"status": "error", "message": "Model download failed."}
    else:
        return {"status": "skipped", "reason": "No valid action provided."}

# Register with RunPod
runpod.serverless.start({"handler": handler})

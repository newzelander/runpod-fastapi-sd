import os
import shutil
from diffusers import StableDiffusion3Pipeline
import torch
import runpod

# Paths
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
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Error deleting {item_path}: {e}")

def flatten_and_move_files(src_dir, dest_dir):
    """
    Navigate through Hugging Face's nested cache structure and move all model files
    directly into the destination directory (without nested directories).
    """
    model_cache_dirs = [
        os.path.join(src_dir, d)
        for d in os.listdir(src_dir)
        if d.startswith("models--") and os.path.isdir(os.path.join(src_dir, d))
    ]

    if not model_cache_dirs:
        print("❌ No model cache directory found.")
        return

    model_cache_dir = model_cache_dirs[0]  # First match is assumed correct
    snapshot_root = os.path.join(model_cache_dir, "snapshots")

    if not os.path.exists(snapshot_root):
        print("❌ No snapshot directory found inside model cache.")
        return

    snapshot_subdirs = os.listdir(snapshot_root)
    if not snapshot_subdirs:
        print("❌ No snapshot subdirectories found.")
        return

    snapshot_path = os.path.join(snapshot_root, snapshot_subdirs[0])
    print(f"📁 Using snapshot path: {snapshot_path}")

    # Move all files directly into the destination directory (MODEL_PATH)
    for root, _, files in os.walk(snapshot_path):
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, file)  # Flatten the directory structure
            shutil.move(src_file, dest_file)
            print(f"✅ Moved {src_file} to {dest_file}")

def get_dir_size(path):
    """Calculate total size of directory in bytes."""
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total

def list_directory_contents(path):
    """Print directory tree."""
    print(f"\n📂 Contents of {path}:")
    for root, dirs, files in os.walk(path):
        level = root.replace(path, "").count(os.sep)
        indent = " " * (4 * level)
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = " " * (4 * (level + 1))
        for f in files:
            print(f"{sub_indent}{f}")

def download_model():
    """Download the model into cache, flatten structure, and move to model path."""
    os.makedirs(MODEL_PATH, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(os.path.join(MODEL_PATH, "model_index.json")):
        print("✅ Model already exists.")
        return StableDiffusion3Pipeline.from_pretrained(MODEL_PATH, torch_dtype=torch.float16)
    else:
        try:
            print("⬇️ Downloading model to cache folder...")
            pipe = StableDiffusion3Pipeline.from_pretrained(
                pretrained_model_name_or_path=MODEL_NAME,
                torch_dtype=torch.float16,
                use_safetensors=True,
                variant="fp16",
                cache_dir=CACHE_DIR
            )

            print(f"✅ Moving model from cache to model path: {MODEL_PATH}...")
            flatten_and_move_files(CACHE_DIR, MODEL_PATH)
            print("✅ Model moved.")

            remove_all(CACHE_DIR)
            print("🧹 Cache cleaned.")

            return pipe

        except Exception as e:
            print(f"❌ Error during model download and move: {e}")
            return None

def display_storage_info():
    """Display the contents and sizes of the model and cache directories."""
    print("\n### Directory Information ###")
    list_directory_contents(MODEL_PATH)
    model_size = get_dir_size(MODEL_PATH)
    print(f"\n📦 Total size of {MODEL_PATH}: {model_size / (1024 * 1024):.2f} MB")

    list_directory_contents(CACHE_DIR)
    cache_size = get_dir_size(CACHE_DIR)
    print(f"\n🧊 Total size of {CACHE_DIR}: {cache_size / (1024 * 1024):.2f} MB")

def handler(job):
    input_data = job.get("input", {})
    if input_data.get("action") == "clean":
        print("💻 Cleaning model and cache folders...")
        remove_all(MODEL_PATH)
        pipe = download_model()

        if pipe is not None:
            display_storage_info()
            return {
                "status": "success",
                "message": "Model downloaded and moved to model path."
            }
        else:
            return {
                "status": "failure",
                "message": "An error occurred during the model download process."
            }
    else:
        print("❌ No valid action provided. Skipping.")
        return {"status": "skipped", "reason": "No valid action provided."}

# Start RunPod serverless handler
runpod.serverless.start({"handler": handler})

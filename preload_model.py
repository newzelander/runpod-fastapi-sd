from huggingface_hub import snapshot_download
import os

MODEL_ID = "stabilityai/stable-diffusion-3.5-large"
CACHE_DIR = "/runpod-volume/models/hf-cache"

def get_or_download_model():
    # Get Hugging Face token from environment
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN is not set.")

    # Download model snapshot to cache (uses symlinks and avoids duplication)
    snapshot_path = snapshot_download(
        repo_id=MODEL_ID,
        cache_dir=CACHE_DIR,
        use_auth_token=hf_token,
        ignore_patterns=["*.msgpack"],  # Optional: skip unneeded files
        local_dir_use_symlinks=True,
    )

    return snapshot_path

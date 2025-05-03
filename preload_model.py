import os
from huggingface_hub import snapshot_download

def download_model(target_path):
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("Hugging Face token is required but not found in environment variables.")

    # Skip download if already present
    if os.path.exists(target_path) and any(os.scandir(target_path)):
        print(f"[INFO] Model already exists at {target_path}, skipping download.")
        return

    print(f"[INFO] Downloading model to {target_path}...")

    snapshot_download(
        repo_id="stabilityai/stable-diffusion-3.5-large",
        local_dir=target_path,
        local_dir_use_symlinks=False,  # Ensures flat structure
        resume_download=True,
        use_auth_token=hf_token
    )

    print(f"[INFO] Download complete.")

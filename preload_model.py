import os
from huggingface_hub import snapshot_download

def download_model(target_path):
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN not found in environment variables.")

    # If model is already downloaded, skip
    if os.path.exists(target_path) and any(os.scandir(target_path)):
        print(f"Model already exists at {target_path}, skipping download.")
        return

    print(f"Downloading model directly to {target_path}...")
    
    snapshot_download(
        repo_id="stabilityai/stable-diffusion-3.5-large",
        local_dir=target_path,
        local_dir_use_symlinks=False,  # Ensure a flat structure
        use_auth_token=hf_token,
        resume_download=True
    )

    print(f"Download complete and model is ready at {target_path}.")

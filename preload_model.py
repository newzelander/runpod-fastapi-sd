import os
from huggingface_hub import snapshot_download

def download_model(target_path):
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN not found in environment variables.")

    # If the model already exists in the target directory, skip downloading
    if os.path.exists(os.path.join(target_path, "model_index.json")):
        print(f"Model already exists at {target_path}")
        return

    print("Downloading model directly to the target folder...")
    snapshot_download(
        repo_id="stabilityai/stable-diffusion-3.5-large",
        cache_dir="/runpod-volume/models",  # Directly set the cache folder to the target directory
        local_dir=target_path,  # Target directory to store the model
        local_dir_use_symlinks=False,  # Ensures flat structure
        use_auth_token=hf_token,
        resume_download=True
    )

    print(f"Model downloaded directly to {target_path}")

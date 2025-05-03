import os
from huggingface_hub import snapshot_download

def download_model(model_path):
    # Get the Hugging Face token from environment variables
    hf_token = os.environ.get("HF_TOKEN")

    if not hf_token:
        raise ValueError("Hugging Face token is required but not found in environment variables.")

    # If the model does not exist in the target path, download it
    if not os.path.exists(model_path):
        print(f"Downloading model to {model_path}...")
        snapshot_download(
            repo_id="stabilityai/stable-diffusion-3.5-large",  # Correct repo_id for the model
            local_dir=model_path,
            local_dir_use_symlinks=False,  # Avoid using symlinks when downloading
            resume_download=True,
            use_auth_token=hf_token  # Use the Hugging Face token for authentication
        )
    else:
        print(f"Model already exists at {model_path}")

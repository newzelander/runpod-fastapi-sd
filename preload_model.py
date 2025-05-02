import os
from huggingface_hub import snapshot_download, login

def download_model(model_path):
    # Authenticate (if token is provided)
    hf_token = os.environ.get("HF_TOKEN")  # Using os.environ.get for the token
    if hf_token:
        login(token=hf_token)

    # If the model does not exist in the target path, download it
    if not os.path.exists(model_path):
        snapshot_download(
            repo_id="stabilityai/stable-diffusion-3.5-large",  # Correct repo_id for the model
            cache_dir=model_path,
            local_dir_use_symlinks=False,
            resume_download=True,
            token=hf_token  # Explicitly include token for better security
        )

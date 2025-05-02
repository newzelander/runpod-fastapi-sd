import os
from huggingface_hub import snapshot_download

def download_model(model_path):
    # If the model does not exist in the target path, download it
    if not os.path.exists(model_path):
        snapshot_download(
            repo_id="stabilityai/stable-diffusion-3.5-large",  # Correct repo_id for the model
            local_dir=model_path,
            local_dir_use_symlinks=False,  # Avoid using symlinks when downloading
            resume_download=True
        )

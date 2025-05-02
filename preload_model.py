import os
from huggingface_hub import snapshot_download

def download_model(model_path):
    token = os.environ.get("HF_TOKEN")  # 🔐 Access token from RunPod Secrets

    if not os.path.exists(model_path):
        snapshot_download(
            repo_id="stabilityai/stable-diffusion-3.5-large",
            cache_dir=model_path,
            local_dir_use_symlinks=False,
            resume_download=True,
            token=token  # ✅ Required for gated/private models
        )

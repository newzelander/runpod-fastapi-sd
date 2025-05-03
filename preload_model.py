import os
from huggingface_hub import snapshot_download

def get_or_download_model(cache_base_dir):
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN is not set.")

    # This path becomes the root Hugging Face cache dir
    snapshot_path = snapshot_download(
        repo_id="stabilityai/stable-diffusion-3.5-large",
        cache_dir=cache_base_dir,
        use_auth_token=hf_token,
        resume_download=True
    )

    return snapshot_path  # this is the actual model path to load later

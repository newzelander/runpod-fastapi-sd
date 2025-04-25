from diffusers import StableDiffusion3Pipeline

# Pre-download and cache the model (this will only happen once)
StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3.5",
    cache_dir="/workspace/models/stable-diffusion-3.5"
)


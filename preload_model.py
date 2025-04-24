from diffusers import StableDiffusion3Pipeline

# Pre-download and cache the model (this will only happen once)
StableDiffusion3Pipeline.from_pretrained(
    stabilityaistable-diffusion-3.5-large, 
    cache_dir=workspacemodelsstable-diffusion-3.5
)

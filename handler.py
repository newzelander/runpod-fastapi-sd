from diffusers import StableDiffusion3Pipeline
import torch
from PIL import Image
import os
import runpod
import uuid

# Path to the snapshot folder where model files are located
SNAPSHOT_PATH = "/runpod-volume/models/stable-diffusion-3.5-large/cache/models--stabilityai--stable-diffusion-3.5-large/snapshots/ceddf0a7fdf2064ea28e2213e3b84e4afa170a0f"

# Output directory
OUTPUT_DIR = "/runpod-volume/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the model from local snapshot with half-precision and memory-efficient config
pipe = StableDiffusion3Pipeline.from_pretrained(
    pretrained_model_name_or_path=SNAPSHOT_PATH,
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16"
).to("cuda")

# Optional: Enable memory optimizations
try:
    pipe.enable_xformers_memory_efficient_attention()
except Exception as e:
    print(f"Xformers not available or failed to enable: {e}")

pipe.enable_attention_slicing()
pipe.safety_checker = None  # Optional: disable safety checker to save VRAM

# Path to base cache folder
BASE_CACHE_PATH = "/runpod-volume/models/stable-diffusion-3.5-large/cache"

# Scan cache directory
def scan_cache_files(base_path):
    file_paths = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

cached_files = scan_cache_files(BASE_CACHE_PATH)
print(f"Files found in cache directory: {cached_files}")

# Handler function
def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")

    if not prompt:
        return {"status": "error", "message": "No prompt provided!"}

    # Generate image with your custom inference settings
    image: Image.Image = pipe(
        prompt=prompt,
        num_inference_steps=28,
        guidance_scale=3.5
    ).images[0]

    # Save image
    file_name = f"{uuid.uuid4().hex}.png"
    image_path = os.path.join(OUTPUT_DIR, file_name)
    image.save(image_path)

    # Create a link assuming volume is publicly exposed
    public_url = f"https://{job['id']}-output.runpod.io/{file_name}"

    return {
        "status": "success",
        "prompt": prompt,
        "image_path": image_path,
        "url": public_url
    }

# Start serverless handler
runpod.serverless.start({"handler": handler})

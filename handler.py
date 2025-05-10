from diffusers import StableDiffusion3Pipeline
import torch
from PIL import Image
import os
import runpod
import uuid

# Path to the snapshot folder where model files are actually located
SNAPSHOT_PATH = "/runpod-volume/models/stable-diffusion-3.5-large/cache/models--stabilityai--stable-diffusion-3.5-large/snapshots/ceddf0a7fdf2064ea28e2213e3b84e4afa170a0f"

# Output directory to save generated image
OUTPUT_DIR = "/runpod-volume/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load model from local snapshot (⚠️ No downloading)
pipe = StableDiffusion3Pipeline.from_pretrained(
    pretrained_model_name_or_path=SNAPSHOT_PATH,
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16"
).to("cuda")

# Path to base cache folder for recursive scanning
BASE_CACHE_PATH = "/runpod-volume/models/stable-diffusion-3.5-large/cache"

# Function to recursively scan files in the cache directory
def scan_cache_files(base_path):
    file_paths = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

# Example of scanning files (you can modify this part as needed)
cached_files = scan_cache_files(BASE_CACHE_PATH)
print(f"Files found in cache directory: {cached_files}")

# Handler function to process the incoming request
def handler(job):
    # Get the prompt from the job input (provided by the RunPod UI)
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")  # No default prompt set here
    
    if not prompt:
        return {"status": "error", "message": "No prompt provided!"}

    # Generate image from the prompt
    image: Image.Image = pipe(prompt).images[0]

    # Save image
    file_name = f"{uuid.uuid4().hex}.png"
    image_path = os.path.join(OUTPUT_DIR, file_name)
    image.save(image_path)

    # Create a simple URL link assuming RunPod will expose this volume path
    public_url = f"https://{job['id']}-output.runpod.io/{file_name}"

    return {
        "status": "success",
        "prompt": prompt,
        "image_path": image_path,
        "url": public_url
    }

# RunPod serverless start
runpod.serverless.start({"handler": handler})

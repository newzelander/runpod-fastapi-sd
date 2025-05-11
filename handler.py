from diffusers import StableDiffusion3Pipeline
import torch
from PIL import Image
import os
import runpod
import uuid
import time
import base64

# Paths
SNAPSHOT_PATH = "/runpod-volume/models/stable-diffusion-3.5-large/cache/models--stabilityai--stable-diffusion-3.5-large/snapshots/ceddf0a7fdf2064ea28e2213e3b84e4afa170a0f"
BASE_CACHE_PATH = "/runpod-volume/models/stable-diffusion-3.5-large/cache"
OUTPUT_DIR = "/runpod-volume/outputs"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Utility to calculate total size of a directory
def get_directory_size(path):
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total

def human_readable_size(bytes, decimals=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.{decimals}f} {unit}"
        bytes /= 1024
    return f"{bytes:.{decimals}f} PB"

# Log sizes of key directories
print(f"📁 SNAPSHOT_PATH size: {human_readable_size(get_directory_size(SNAPSHOT_PATH))}")
print(f"📁 BASE_CACHE_PATH size: {human_readable_size(get_directory_size(BASE_CACHE_PATH))}")
print(f"📁 OUTPUT_DIR size: {human_readable_size(get_directory_size(OUTPUT_DIR))}")

# Load the pipeline from local
print("🚀 Loading Stable Diffusion pipeline from local paths...")
load_start = time.time()

pipe = StableDiffusion3Pipeline.from_pretrained(
    pretrained_model_name_or_path=SNAPSHOT_PATH,
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16",
    cache_dir=BASE_CACHE_PATH
).to("cuda")

load_end = time.time()
print(f"✅ Model loaded in {load_end - load_start:.2f} seconds")

# Memory optimizations
try:
    pipe.enable_xformers_memory_efficient_attention()
    print("✅ Xformers memory optimization enabled")
except Exception as e:
    print(f"⚠️ Xformers optimization failed: {e}")

pipe.enable_attention_slicing()
pipe.safety_checker = None
print("🧠 Attention slicing enabled; safety checker disabled")

# Handler function
def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")

    if not prompt:
        return {"status": "error", "message": "No prompt provided."}

    print(f"🎨 Generating image for prompt: {prompt}")
    generation_start = time.time()

    image: Image.Image = pipe(
        prompt=prompt,
        num_inference_steps=28,
        guidance_scale=3.5
    ).images[0]

    generation_end = time.time()
    print(f"✅ Image generated in {generation_end - generation_start:.2f} seconds")

    # Save and encode image
    file_name = f"{uuid.uuid4().hex}.png"
    image_path = os.path.join(OUTPUT_DIR, file_name)
    image.save(image_path)

    with open(image_path, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        image_data_url = f"data:image/png;base64,{image_base64}"

    return {
        "status": "success",
        "prompt": prompt,
        "image_base64": image_data_url,
        "html": f'<a download="image.png" href="{image_data_url}">Download Image</a>'
    }

# Start the serverless handler
print("🟢 Ready to accept jobs")
runpod.serverless.start({"handler": handler})

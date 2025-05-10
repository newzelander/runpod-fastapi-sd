from diffusers import StableDiffusion3Pipeline 
import torch
from PIL import Image
import os
import runpod
import uuid
import time
import base64  # <-- added for image preview

# Path to the snapshot folder where model files are located
SNAPSHOT_PATH = "/runpod-volume/models/stable-diffusion-3.5-large/cache/models--stabilityai--stable-diffusion-3.5-large/snapshots/ceddf0a7fdf2064ea28e2213e3b84e4afa170a0f"

# Output directory
OUTPUT_DIR = "/runpod-volume/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Path to base cache folder
BASE_CACHE_PATH = "/runpod-volume/models/stable-diffusion-3.5-large/cache"

# Function to scan and get all model files in a directory
def scan_cache_files(base_path):
    file_paths = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            full_path = os.path.join(root, file)
            file_paths.append(full_path)
    return file_paths

# Check files in snapshot path and cache
print("🔍 Scanning snapshot and cache directories...")
cached_files = scan_cache_files(BASE_CACHE_PATH)
snapshot_files = scan_cache_files(SNAPSHOT_PATH)

# Log number of files found
print(f"✅ {len(snapshot_files)} files found in SNAPSHOT_PATH")
print(f"✅ {len(cached_files)} files found in BASE_CACHE_PATH before merging")

# Merge snapshot files into cached list
for file in snapshot_files:
    if file not in cached_files:
        cached_files.append(file)

print(f"🗃️ Total unique model files after merge: {len(cached_files)}")
print("📂 Snapshot files:")
for path in snapshot_files:
    print(f" - {path}")

print("📂 Final cache files used:")
for path in cached_files:
    print(f" - {path}")

# Load the model from the local snapshot folder and explicitly avoid downloading anything
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
print(f"✅ Model loaded successfully in {load_end - load_start:.2f} seconds")

# Optional: Enable memory optimizations
try:
    pipe.enable_xformers_memory_efficient_attention()
    print("✅ Xformers memory optimization enabled")
except Exception as e:
    print(f"⚠️ Xformers not available or failed to enable: {e}")

pipe.enable_attention_slicing()
pipe.safety_checker = None  # Optional: disable safety checker to save VRAM
print("🧠 Attention slicing enabled; safety checker disabled")

# Handler function
def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")

    if not prompt:
        return {"status": "error", "message": "No prompt provided!"}

    print(f"🎨 Received prompt: '{prompt}' — starting generation...")

    # Generate image with your custom inference settings
    generation_start = time.time()
    image: Image.Image = pipe(
        prompt=prompt,
        num_inference_steps=28,
        guidance_scale=3.5
    ).images[0]
    generation_end = time.time()

    print(f"✅ Image generated in {generation_end - generation_start:.2f} seconds")

    # Save image
    file_name = f"{uuid.uuid4().hex}.png"
    image_path = os.path.join(OUTPUT_DIR, file_name)
    image.save(image_path)
    print(f"🖼️ Image saved to: {image_path}")

    # Read and encode the image as base64 to preview it in RunPod UI
    with open(image_path, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    # Create a link assuming volume is publicly exposed
    public_url = f"https://{job['id']}-output.runpod.io/{file_name}"

    return {
        "status": "success",
        "prompt": prompt,
        "image_path": image_path,
        "url": public_url,
        "image_base64": image_base64  # 👈 RunPod will show this directly as a preview
    }

# Start serverless handler
print("🟢 Ready to accept jobs")
runpod.serverless.start({"handler": handler})

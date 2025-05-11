from diffusers import StableDiffusion3Pipeline
import torch
from PIL import Image
import os
import runpod
import uuid
import time
import base64  # For base64 image preview

# Paths
SNAPSHOT_PATH = "/runpod-volume/models/stable-diffusion-3.5-large/cache/models--stabilityai--stable-diffusion-3.5-large/snapshots/ceddf0a7fdf2064ea28e2213e3b84e4afa170a0f"
OUTPUT_DIR = "/runpod-volume/outputs"
BASE_CACHE_PATH = "/runpod-volume/models/stable-diffusion-3.5-large/cache"

# Create output directory if not exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to scan all files in a directory
def scan_cache_files(base_path):
    file_paths = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            full_path = os.path.join(root, file)
            file_paths.append(full_path)
    return file_paths

# Function to get total directory size in MB
def get_directory_size_mb(path):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return round(total_size / (1024 * 1024), 2)  # Convert to MB

# Scan directories
print("🔍 Scanning snapshot and cache directories...")
cached_files = scan_cache_files(BASE_CACHE_PATH)
snapshot_files = scan_cache_files(SNAPSHOT_PATH)

print(f"✅ {len(snapshot_files)} files found in SNAPSHOT_PATH")
print(f"✅ {len(cached_files)} files found in BASE_CACHE_PATH before merging")

# Merge snapshot files into cached list
for file in snapshot_files:
    if file not in cached_files:
        cached_files.append(file)

print(f"🗃️ Total unique model files after merge: {len(cached_files)}")

# Show some files (optional)
print("📂 Snapshot files:")
for path in snapshot_files[:3]:
    print(f" - {path}")
if len(snapshot_files) > 3:
    print(" - ...")

print("📂 Final cache files used:")
for path in cached_files[:3]:
    print(f" - {path}")
if len(cached_files) > 3:
    print(" - ...")

# Report sizes of directories
print("\n📦 Directory Sizes:")
print(f"📁 SNAPSHOT_PATH size: {get_directory_size_mb(SNAPSHOT_PATH)} MB")
print(f"📁 BASE_CACHE_PATH size: {get_directory_size_mb(BASE_CACHE_PATH)} MB")
print(f"📁 OUTPUT_DIR (generated images): {get_directory_size_mb(OUTPUT_DIR)} MB\n")

# Load the model
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
pipe.safety_checker = None  # Disable safety checker to save VRAM
print("🧠 Attention slicing enabled; safety checker disabled")

# Handler function
def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")

    if not prompt:
        return {"status": "error", "message": "No prompt provided!"}

    print(f"🎨 Received prompt: '{prompt}' — starting generation...")

    generation_start = time.time()
    image: Image.Image = pipe(
        prompt=prompt,
        num_inference_steps=28,
        guidance_scale=3.5
    ).images[0]
    generation_end = time.time()

    print(f"✅ Image generated in {generation_end - generation_start:.2f} seconds")

    file_name = f"{uuid.uuid4().hex}.png"
    image_path = os.path.join(OUTPUT_DIR, file_name)
    image.save(image_path)
    print(f"🖼️ Image saved to: {image_path}")

    with open(image_path, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    image_base64 = f"data:image/png;base64,{image_base64}"

    public_url = f"https://{job['id']}-output.runpod.io/{file_name}"

    return {
        "status": "success",
        "prompt": prompt,
        "image_path": image_path,
        "url": public_url,
        "image_base64": image_base64
    }

# Start serverless handler
print("🟢 Ready to accept jobs")
runpod.serverless.start({"handler": handler})

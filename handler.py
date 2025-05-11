from huggingface_hub import InferenceClient
import uuid
import time
import base64
import os
import runpod
import traceback

# Read Hugging Face token from environment variable
HF_TOKEN = os.environ.get("HF_TOKEN")

if not HF_TOKEN:
    print("❌ ERROR: HF_TOKEN environment variable is not set.")
else:
    print("🔑 HF_TOKEN successfully loaded from environment.")

# Define the Hugging Face model ID
MODEL_ID = "stabilityai/stable-diffusion-3.5-large"

try:
    # Initialize Hugging Face Inference Client
    client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)
    print(f"🧠 Hugging Face client initialized with model: {MODEL_ID}")
except Exception as e:
    print(f"❌ Failed to initialize Hugging Face client: {e}")
    traceback.print_exc()

# Create output directory
OUTPUT_DIR = "/runpod-volume/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Directory size logging
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

print(f"📁 OUTPUT_DIR size: {human_readable_size(get_directory_size(OUTPUT_DIR))}")

# Main handler
def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")

    if not prompt:
        print("⚠️ No prompt provided in input.")
        return {"status": "error", "message": "No prompt provided."}

    print(f"🎨 Generating image for prompt: {prompt}")
    generation_start = time.time()

    try:
        # Image generation
        image = client.text_to_image(prompt=prompt, num_inference_steps=28, guidance_scale=3.5)
        generation_end = time.time()
        print(f"✅ Image generated in {generation_end - generation_start:.2f} seconds")

        # File saving
        file_name = f"{uuid.uuid4().hex}.png"
        image_path = os.path.join(OUTPUT_DIR, file_name)
        image.save(image_path)
        print(f"💾 Image saved to: {image_path}")

        # Base64 encode image
        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
            image_data_url = f"data:image/png;base64,{image_base64}"

        return {
            "status": "success",
            "prompt": prompt,
            "image_base64": image_data_url,
            "html": f'<a download="image.png" href="{image_data_url}">Download Image</a>'
        }

    except Exception as e:
        print(f"❌ ERROR during image generation or processing: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": "Image generation failed. See server logs for details.",
            "error": str(e)
        }

# Start the serverless job handler
print("🟢 Ready to accept jobs from RunPod...")
runpod.serverless.start({"handler": handler})

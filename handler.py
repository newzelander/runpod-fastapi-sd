from huggingface_hub import InferenceClient
import uuid
import time
import base64
import os
import runpod

# Read Hugging Face token from environment variable
HF_TOKEN = os.environ.get("HF_TOKEN")  # Make sure this matches your RunPod secret key name

# Define the Hugging Face model ID
MODEL_ID = "stabilityai/stable-diffusion-3.5-large"

# Hugging Face Inference API client setup with token
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

# Paths
OUTPUT_DIR = "/runpod-volume/outputs"
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

print(f"📁 OUTPUT_DIR size: {human_readable_size(get_directory_size(OUTPUT_DIR))}")

# Handler function
def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")

    if not prompt:
        return {"status": "error", "message": "No prompt provided."}

    print(f"🎨 Generating image for prompt: {prompt}")
    generation_start = time.time()

    # Call Hugging Face inference API
    image = client.text_to_image(prompt=prompt, num_inference_steps=28, guidance_scale=3.5)

    generation_end = time.time()
    print(f"✅ Image generated in {generation_end - generation_start:.2f} seconds")

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

print("🟢 Ready to accept jobs")
runpod.serverless.start({"handler": handler})

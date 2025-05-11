from huggingface_hub import InferenceClient
import uuid
import time
import base64
import os
import runpod

# Define the Hugging Face model ID (you can replace this with your model's ID)
MODEL_ID = "stabilityai/stable-diffusion-3.5-large"  # Example, replace with your model's ID

# Hugging Face Inference API client setup
client = InferenceClient(model=MODEL_ID)

# Paths
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

# Log size of OUTPUT_DIR
print(f"📁 OUTPUT_DIR size: {human_readable_size(get_directory_size(OUTPUT_DIR))}")

# Handler function
def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")

    if not prompt:
        return {"status": "error", "message": "No prompt provided."}

    print(f"🎨 Generating image for prompt: {prompt}")
    generation_start = time.time()

    # Call Hugging Face's inference API to generate the image
    response = client.text_to_image(prompt=prompt, num_inference_steps=28, guidance_scale=3.5)

    generation_end = time.time()
    print(f"✅ Image generated in {generation_end - generation_start:.2f} seconds")

    # Save and encode image
    file_name = f"{uuid.uuid4().hex}.png"
    image_path = os.path.join(OUTPUT_DIR, file_name)
    image = response['image']  # Assuming Hugging Face returns image in some format

    with open(image_path, "wb") as img_file:
        img_file.write(image)

    # Encode image to base64
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

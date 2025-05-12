import uuid
import time
import base64
import os
import runpod
import traceback
import requests
from urllib.parse import quote

OUTPUT_DIR = "/runpod-volume/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")

    if not prompt:
        print("⚠️ No prompt provided in input.")
        return {"status": "error", "message": "No prompt provided."}

    print(f"🎨 Generating image for prompt: {prompt}")
    generation_start = time.time()

    try:
        # URL-encode the prompt
        encoded_prompt = quote(prompt)

        # Build the request URL
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true&private=true"

        # Send the GET request to Pollinations.ai
        response = requests.get(url)
        response.raise_for_status()

        # Save the image
        file_name = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(OUTPUT_DIR, file_name)
        with open(image_path, "wb") as f:
            f.write(response.content)

        generation_end = time.time()
        print(f"✅ Image generated in {generation_end - generation_start:.2f} seconds")
        print(f"💾 Image saved to: {image_path} ({human_readable_size(os.path.getsize(image_path))})")

        # Encode the image to base64
        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
            image_data_url = f"data:image/jpeg;base64,{image_base64}"

        return {
            "status": "success",
            "prompt": prompt,
            "image_base64": image_data_url,
            "html": f'<a download="image.jpg" href="{image_data_url}">Download Image</a>'
        }

    except Exception as e:
        print(f"❌ ERROR during image generation or processing: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": "Image generation failed. See server logs for details.",
            "error": str(e)
        }

print("🟢 Ready to accept jobs from RunPod...")
runpod.serverless.start({"handler": handler})

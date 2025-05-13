import os
import uuid
import base64
import requests
import runpod
import traceback
import json

# Directory where output images will be saved
OUTPUT_DIR = "/runpod-volume/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cloudflare credentials
CF_API_KEY = os.environ.get("CF_API_KEY")
CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID") or "48e7ad58d6c738dfa0e4d609249df2a3"

def handler(job):
    input_data = job.get("input", {})

    prompt = input_data.get("prompt", "").strip()
    negative_prompt = input_data.get("negative_prompt", "").strip()

    if not prompt:
        return {"status": "error", "message": "No prompt provided."}

    if not CF_API_KEY or not CF_ACCOUNT_ID:
        return {"status": "error", "message": "Missing Cloudflare API credentials."}

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt
    }

    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {CF_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print(f"🎨 Sending request to Cloudflare: {url}")
        response = requests.post(url, headers=headers, json=payload)

        print("🔍 Status code:", response.status_code)
        print("🔍 Response text:", response.text)

        response.raise_for_status()
        result = response.json()

        # Cloudflare wraps the AI output inside 'result' -> 'image'
        image_base64 = result.get("result", {}).get("image")

        if not image_base64:
            return {"status": "error", "message": "No image returned from Cloudflare AI."}

        # Decode and save image
        image_data = base64.b64decode(image_base64)
        file_name = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(OUTPUT_DIR, file_name)

        with open(image_path, "wb") as f:
            f.write(image_data)

        image_data_url = f"data:image/jpeg;base64,{image_base64}"

        return {
            "status": "success",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_path": image_path,
            "image_base64": image_data_url,
            "html": f'<a download="image.jpg" href="{image_data_url}">Download Image</a>'
        }

    except Exception as e:
        print("❌ Exception occurred:")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

print("🟢 Worker is ready to receive jobs via RunPod...")
runpod.serverless.start({"handler": handler})

import os
import uuid
import base64
import requests
import runpod
import traceback

OUTPUT_DIR = "/runpod-volume/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CF_API_KEY = os.environ.get("CF_API_KEY")
CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")

def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt", "").strip()
    negative_prompt = input_data.get("negative_prompt", "").strip()

    if not prompt:
        return {"status": "error", "message": "No prompt provided."}

    if not CF_API_KEY or not CF_ACCOUNT_ID:
        return {"status": "error", "message": "Missing Cloudflare API credentials in environment variables."}

    # Build the payload for Cloudflare's AI API
    input_payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": 1024,                # hardcoded value for image width
        "height": 1024,               # hardcoded value for image height
        "num_inference_steps": 35,    # hardcoded inference steps
        "guidance_scale": 7.5         # hardcoded guidance scale
    }

    payload = {
        "input": input_payload
    }

    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {CF_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print(f"🎨 Sending request to Cloudflare Workers AI: {url}")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        if "result" not in result or "image" not in result["result"]:
            return {"status": "error", "message": "Image not returned by Cloudflare API."}

        image_base64 = result["result"]["image"]
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
            "image_base64": image_data_url,
            "html": f'<a download="image.jpg" href="{image_data_url}">Download Image</a>'
        }

    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

print("🟢 Ready to accept jobs from RunPod using Cloudflare Workers AI...")
runpod.serverless.start({"handler": handler})

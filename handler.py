import os
import uuid
import requests
import runpod
import traceback
import json
import base64  # For base64 encoding

# Directory where output images will be saved
OUTPUT_DIR = "/runpod-volume/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load credentials from environment variables
CF_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
CF_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

def handler(job):
    input_data = job.get("input", {})

    prompt = input_data.get("prompt", "").strip()
    negative_prompt = input_data.get("negative_prompt", "").strip()

    if not prompt:
        return {"status": "error", "message": "No prompt provided."}

    if not CF_API_TOKEN or not CF_ACCOUNT_ID:
        return {"status": "error", "message": "Missing Cloudflare API credentials."}

    # Payload for Cloudflare AI (using Flux model)
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt
    }

    # URL for the Flux model (latest model from Cloudflare)
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/flux/image-generation"

    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        print(f"🎨 Sending request to Cloudflare: {url}")
        response = requests.post(url, headers=headers, json=payload)

        print("🔍 Status code:", response.status_code)
        print("🔍 Response text:", response.text[:500])  # Only for debugging

        # Check if the request failed
        response.raise_for_status()

        # Ensure response contains image data
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            return {"status": "error", "message": f"Expected image, but got: {content_type}"}

        image_data = response.content
        if not image_data:
            return {"status": "error", "message": "No image returned from Cloudflare AI."}

        # Save image
        file_name = f"{uuid.uuid4().hex}.png"
        image_path = os.path.join(OUTPUT_DIR, file_name)
        with open(image_path, "wb") as f:
            f.write(image_data)

        # Create base64 version
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        data_url = f"data:image/png;base64,{image_base64}"

        return {
            "status": "success",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_path": image_path,
            "image_base64": data_url,
            "html": f'<a download="image.png" href="{data_url}">Download Image</a>'
        }

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return {"status": "error", "message": f"HTTP error: {http_err}"}
    except Exception as e:
        print("❌ Exception occurred:")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

print("🟢 Worker is ready to receive jobs via RunPod...")
runpod.serverless.start({"handler": handler})

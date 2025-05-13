import os
import uuid
import requests
import runpod
import traceback
import json
import base64  # Add this for base64 encoding

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
        print("🔍 Response text:", response.text[:500])  # Limit to 500 chars for safety

        # Handle any HTTP error response (e.g., 400 or 500)
        response.raise_for_status()

        # Check if the response content is what we expect (e.g., an image)
        content_type = response.headers.get("Content-Type")
        if "image" not in content_type:
            return {"status": "error", "message": f"Expected image, but got {content_type}"}

        # The image is returned as a binary response, not JSON
        image_data = response.content  # Binary data of the image

        if not image_data:
            return {"status": "error", "message": "No image returned from Cloudflare AI."}

        file_name = f"{uuid.uuid4().hex}.png"  # Save as PNG since it seems to be a PNG image
        image_path = os.path.join(OUTPUT_DIR, file_name)

        with open(image_path, "wb") as f:
            f.write(image_data)

        # Return a download link for the image
        image_data_url = f"data:image/png;base64,{base64.b64encode(image_data).decode('utf-8')}"

        return {
            "status": "success",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_path": image_path,
            "image_base64": image_data_url,
            "html": f'<a download="image.png" href="{image_data_url}">Download Image</a>'
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

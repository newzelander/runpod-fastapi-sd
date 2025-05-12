import requests
import os
import uuid
import time
import base64
import traceback
import runpod  # ✅ Required for runpod.serverless

# Load API key from environment variables
AI_HORDE_API_KEY = os.environ.get("AI_HORDE_API_KEY")
if not AI_HORDE_API_KEY:
    print("❌ ERROR: AI_HORDE_API_KEY environment variable is not set.")
else:
    print("🔑 AI_HORDE_API_KEY successfully loaded from environment.")

# AI Horde API URL for async generation
AI_HORDE_API_URL = "https://aihorde.net/api/v2/generate/async"

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
        # Prepare the payload for AI Horde
        payload = {
            "prompt": prompt,
            "models": ["stable_cascade"],  # Make sure this model is valid on AI Horde
            "num_inference_steps": 50,
            "guidance_scale": 7.5
        }

        # ✅ Corrected headers to use 'apikey'
        headers = {
            'apikey': AI_HORDE_API_KEY,
            'Content-Type': 'application/json'
        }

        # Send request to AI Horde API
        response = requests.post(AI_HORDE_API_URL, json=payload, headers=headers)

        # Raise an error for bad responses (e.g., 400, 401)
        response.raise_for_status()

        # Process the response
        image_data = response.json()
        image_url = image_data.get("url")

        if not image_url:
            raise ValueError("No image URL received from AI Horde.")

        # Download the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        file_name = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(OUTPUT_DIR, file_name)

        with open(image_path, "wb") as img_file:
            img_file.write(image_response.content)

        print(f"💾 Image saved to: {image_path} ({human_readable_size(os.path.getsize(image_path))})")

        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
            image_data_url = f"data:image/jpeg;base64,{image_base64}"

        return {
            "status": "success",
            "prompt": prompt,
            "image_base64": image_data_url,
            "html": f'<a download="image.jpg" href="{image_data_url}">Download Image</a>'
        }

    except requests.exceptions.HTTPError as e:
        error_response = e.response.json()
        print(f"❌ ERROR: {e}")
        print(f"Error Response: {error_response}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
            "error_details": error_response
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

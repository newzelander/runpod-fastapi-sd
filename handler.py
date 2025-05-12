import os
import time
import base64
import uuid
import requests
import traceback
import runpod

# Configuration
OUTPUT_DIR = "./output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

AI_HORDE_API_KEY = os.getenv("AI_HORDE_API_KEY")
AI_HORDE_API_URL = "https://aihorde.net/api/v2/generate/async"

if not AI_HORDE_API_KEY:
    raise EnvironmentError("AI_HORDE_API_KEY not set in environment variables.")

def human_readable_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")

    if not prompt:
        print("⚠️ No prompt provided in input.")
        return {"status": "error", "message": "No prompt provided."}

    print(f"🎨 Generating image for prompt: {prompt}")
    generation_start = time.time()

    try:
        payload = {
            "prompt": prompt,
            "models": ["stable-cascade"],
            "params": {
                "n": 1,
                "steps": 50,
                "width": 512,
                "height": 512,
                "karras": True,
                "sampler_name": "k_euler",
                "cfg_scale": 7
            }
        }

        headers = {
            'apikey': AI_HORDE_API_KEY,
            'Content-Type': 'application/json'
        }

        # Submit async request
        response = requests.post(AI_HORDE_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        request_id = response.json().get("id")

        if not request_id:
            raise ValueError("No request ID received from AI Horde.")

        # Poll for completion
        status_url = f"https://aihorde.net/api/v2/generate/status/{request_id}"
        print(f"⏳ Waiting for image to be generated...")

        while True:
            poll = requests.get(status_url, headers=headers)
            poll.raise_for_status()
            poll_data = poll.json()

            if poll_data.get("done"):
                generations = poll_data.get("generations", [])
                if not generations or "img" not in generations[0]:
                    raise ValueError("No image returned after generation completed.")
                image_url = generations[0]["img"]
                break

            time.sleep(2)  # Delay before next poll

        # Download the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        file_name = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(OUTPUT_DIR, file_name)

        with open(image_path, "wb") as f:
            f.write(image_response.content)

        print(f"💾 Image saved to: {image_path} ({human_readable_size(os.path.getsize(image_path))})")

        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
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
            "message": "Image generation failed.",
            "error": str(e)
        }

# Start RunPod serverless
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})

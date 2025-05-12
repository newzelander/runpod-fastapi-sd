import os
import requests
import time
import uuid
import base64
import runpod
import traceback

# Read API key securely from environment
API_KEY = os.environ.get("AI_HORDE_API_KEY")
if not API_KEY:
    raise EnvironmentError("❌ AI_HORDE_API_KEY environment variable is not set!")

print("🔑 AI_HORDE_API_KEY successfully loaded from environment.")

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
        return {"status": "error", "message": "No prompt provided."}

    print(f"🎨 Generating image for prompt: {prompt}")
    generation_start = time.time()

    try:
        # Submit generation request to AI Horde
        payload = {
            "prompt": prompt,
            "params": {
                "width": 512,
                "height": 512,
                "karras": True,
                "steps": 20,
                "n": 1,
                "sampler_name": "k_euler_ancestral",
                "cfg_scale": 7.5,
                "models": ["stable_cascade"],  # Using Stable Cascade model
                "nsfw": False,
                "trusted_workers": True
            }
        }

        headers = {
            "apikey": API_KEY,
            "client_agent": "runpod-script/1.0"
        }

        print("📤 Sending generation request to AI Horde...")
        submit_response = requests.post("https://aihorde.net/api/v2/generate/async", json=payload, headers=headers)
        submit_response.raise_for_status()

        request_id = submit_response.json().get("id")
        print(f"📬 Request accepted, ID: {request_id}")

        # Poll until the image is ready
        while True:
            poll_response = requests.get(f"https://aihorde.net/api/v2/generate/status/{request_id}", headers=headers)
            poll_response.raise_for_status()
            status = poll_response.json()

            if status.get("done"):
                break
            print("⏳ Waiting for image...")
            time.sleep(2)

        # Download the image
        image_url = status["generations"][0]["img"]
        image_data = requests.get(image_url).content

        file_name = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(OUTPUT_DIR, file_name)

        with open(image_path, "wb") as f:
            f.write(image_data)

        print(f"✅ Image saved to: {image_path} ({human_readable_size(os.path.getsize(image_path))})")

        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
            image_data_url = f"data:image/jpeg;base64,{image_base64}"

        generation_end = time.time()
        print(f"🕒 Total generation time: {generation_end - generation_start:.2f} seconds")

        return {
            "status": "success",
            "prompt": prompt,
            "image_base64": image_data_url,
            "html": f'<a download="image.jpg" href="{image_data_url}">Download Image</a>'
        }

    except Exception as e:
        print(f"❌ ERROR: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }

print("🟢 Ready to accept jobs from RunPod...")
runpod.serverless.start({"handler": handler})

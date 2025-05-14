import requests
import uuid
import base64
import os
import runpod
import traceback

OUTPUT_DIR = "/runpod-volume/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt", "").strip()
    negative_prompt = input_data.get("negative_prompt", "").strip()

    if not prompt:
        print("⚠️ No prompt provided in input.")
        return {"status": "error", "message": "No prompt provided."}

    # Use the flux model from Pollinations with watermark disabled
    base_url = "https://image.pollinations.ai/prompt/"
    prompt_encoded = requests.utils.quote(prompt)
    url = f"{base_url}{prompt_encoded}?model=flux&nologo=true"

    if negative_prompt:
        neg_encoded = requests.utils.quote(negative_prompt)
        url += f"&negPrompt={neg_encoded}"

    print(f"🎨 Generating image from Pollinations API...\nURL: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()

        # Save image
        file_name = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(OUTPUT_DIR, file_name)

        with open(image_path, "wb") as f:
            f.write(response.content)

        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
            image_data_url = f"data:image/jpeg;base64,{image_base64}"

        print(f"✅ Image saved to {image_path}")
        return {
            "status": "success",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_base64": image_data_url,
            "html": f'<a download="image.jpg" href="{image_data_url}">Download Image</a>'
        }

    except Exception as e:
        print(f"❌ ERROR during image generation or download: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": "Image generation failed. See server logs for details.",
            "error": str(e)
        }

print("🟢 Ready to accept jobs from RunPod...")
runpod.serverless.start({"handler": handler})

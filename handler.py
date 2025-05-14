import requests
import uuid
import base64
import runpod
import traceback

def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt", "").strip()
    negative_prompt = input_data.get("negative_prompt", "").strip()

    if not prompt:
        print("⚠️ No prompt provided in input.")
        return {"status": "error", "message": "No prompt provided."}

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

        image_base64 = base64.b64encode(response.content).decode("utf-8")
        image_data_url = f"data:image/jpeg;base64,{image_base64}"

        print("✅ Image fetched and encoded in memory.")
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

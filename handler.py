from optimum.intel.openvino import OVPipelineForText2Image
import uuid
import time
import base64
import os
import runpod
import traceback

# Check if the Hugging Face token is set in the environment
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    print("❌ ERROR: HF_TOKEN environment variable is not set.")
else:
    print("🔑 HF_TOKEN successfully loaded from environment.")

# Set the Hugging Face model ID
MODEL_ID = "AIFunOver/stable-diffusion-3.5-large-turbo-openvino-fp16"

# Output path
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

# Load OpenVINO pipeline
try:
    pipe = OVPipelineForText2Image.from_pretrained(MODEL_ID, use_auth_token=HF_TOKEN)
    print(f"🧠 OpenVINO pipeline loaded with model: {MODEL_ID}")
except Exception as e:
    print(f"❌ Failed to load OpenVINO model: {e}")
    traceback.print_exc()

# Job handler
def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")

    if not prompt:
        print("⚠️ No prompt provided in input.")
        return {"status": "error", "message": "No prompt provided."}

    print(f"🎨 Generating image for prompt: {prompt}")
    generation_start = time.time()

    try:
        image = pipe(prompt=prompt).images[0]  # OpenVINO returns a list
        generation_end = time.time()
        print(f"✅ Image generated in {generation_end - generation_start:.2f} seconds")

        file_name = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(OUTPUT_DIR, file_name)
        image.save(image_path, format="JPEG", quality=85)
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

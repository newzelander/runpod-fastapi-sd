import os
import uuid
import time
import base64
import runpod
import traceback

from optimum.intel.openvino import OVStableDiffusionPipeline
from diffusers.utils import load_image
from PIL import Image

HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    print("❌ ERROR: HF_TOKEN environment variable is not set.")
else:
    print("🔑 HF_TOKEN successfully loaded from environment.")

MODEL_ID = "AIFunOver/stable-diffusion-3.5-large-turbo-openvino-fp16"
OUTPUT_DIR = "/runpod-volume/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the pipeline (without export=True to avoid broken model structure)
pipe = None
try:
    print(f"🔄 Loading pipeline from model: {MODEL_ID}")
    pipe = OVStableDiffusionPipeline.from_pretrained(MODEL_ID, token=HF_TOKEN)
    print("✅ OpenVINO pipeline initialized")
except Exception as e:
    print(f"❌ Failed to load pipeline: {e}")
    traceback.print_exc()

def human_readable_size(bytes, decimals=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.{decimals}f} {unit}"
        bytes /= 1024
    return f"{bytes:.{decimals}f} PB"

def handler(job):
    input_data = job.get("input", {})
    prompt = input_data.get("prompt")

    if not prompt:
        print("⚠️ No prompt provided in input.")
        return {"status": "error", "message": "No prompt provided."}

    if pipe is None:
        print("❌ Pipeline is not initialized.")
        return {"status": "error", "message": "Pipeline is not loaded."}

    print(f"🎨 Generating image for prompt: {prompt}")
    generation_start = time.time()

    try:
        result = pipe(prompt=prompt, num_inference_steps=20, guidance_scale=2.5)
        image = result.images[0]

        generation_end = time.time()
        print(f"✅ Image generated in {generation_end - generation_start:.2f} seconds")

        file_name = f"{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(OUTPUT_DIR, file_name)
        image.save(image_path, format="JPEG", quality=85)

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
            "message": "Image generation failed.",
            "error": str(e)
        }

print("🟢 Ready to accept jobs from RunPod...")
runpod.serverless.start({"handler": handler})

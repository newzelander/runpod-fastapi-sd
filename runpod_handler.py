import os
import runpod
import torch
from diffusers import StableDiffusion3Pipeline
from io import BytesIO
import base64

MODEL_DIR = "/workspace/models/stable-diffusion-3.5"

# Check if the model exists in the persistent volume cache
if not os.path.exists(MODEL_DIR):
    raise FileNotFoundError(f"Model not found in the RunPod persistent volume cache at {MODEL_DIR}. Please preload the model.")

# Load the model
pipe = StableDiffusion3Pipeline.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.float16
).to("cuda")
pipe.enable_attention_slicing()

def handler(job):
    prompt = job["input"].get("prompt")
    if not prompt:
        return {"error": "No prompt provided."}

    try:
        image = pipe(prompt, num_inference_steps=50, guidance_scale=7.5).images[0]
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        base64_img = base64.b64encode(img_bytes.read()).decode("utf-8")
        return {"image_base64": base64_img}
    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})

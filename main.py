import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import torch
from diffusers import StableDiffusion3Pipeline
import base64
from io import BytesIO
import time

app = FastAPI()

# Updated model path to match RunPod serverless volume location
MODEL_DIR = "/runpod-volume/models/stable-diffusion-3.5-large"

class PromptRequest(BaseModel):
    prompt: str

print("⏳ Loading model from persistent volume...")
pipe = StableDiffusion3Pipeline.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.float16,
).to("cuda")
pipe.enable_attention_slicing()
print("✅ Model loaded into memory.")

@app.get("/")
async def root():
    return {"message": "FastAPI is running with local model!"}

@app.post("/runsync")
async def generate_image_endpoint(data: PromptRequest):
    try:
        image = pipe(data.prompt, num_inference_steps=50, guidance_scale=7.5).images[0]
        
        # Convert image to base64 (data URL format)
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        base64_img = base64.b64encode(img_bytes.read()).decode("utf-8")
        
        # Save image to RunPod persistent volume (Updated path)
        timestamp = int(time.time())  # Using timestamp to ensure a unique filename
        image_path = f"/runpod-volume/images/generated_image_{timestamp}.png"  # Updated path
        
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(base64_img))

        # Make the image available for 24 hours (expire time can be adjusted)
        expire_time = timestamp + 86400  # 24 hours later

        # Create the data URL for image
        data_url = f"data:image/png;base64,{base64_img}"

        # URL to access the image directly in the output (for downloading)
        download_link = f"https://runpod.io/storage/{image_path}"

        return JSONResponse(content={
            "image_data_url": data_url,
            "download_link": download_link,
            "image_expiry_time": expire_time
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

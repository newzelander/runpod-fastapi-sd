import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import torch
from diffusers import StableDiffusionPipeline
import base64
from io import BytesIO

app = FastAPI()

# Setup persistent model path
MODEL_DIR = "/workspace/models/stable-diffusion-3.5"

class PromptRequest(BaseModel):
    prompt: str

# Load model once on app start
print("⏳ Loading model from persistent volume...")
pipe = StableDiffusionPipeline.from_pretrained(
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
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        base64_img = base64.b64encode(img_bytes.read()).decode("utf-8")
        return JSONResponse(content={"image_base64": base64_img})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

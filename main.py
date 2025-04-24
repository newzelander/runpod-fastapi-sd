import os
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from diffusers import StableDiffusion3Pipeline
from fastapi.responses import JSONResponse
from io import BytesIO
from PIL import Image
import base64
import uuid

app = FastAPI()

# Set model directory to use persistent volume
MODEL_DIR = "/runpod-volume/stable-diffusion-3.5"

token = os.getenv("HF_TOKEN")

if not token:
    raise ValueError("Hugging Face token is missing. Please set it as an environment variable.")

pipe = None

# Prevent memory fragmentation
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"

@app.on_event("startup")
async def load_model():
    global pipe
    if pipe is None:
        print("Downloading model (once only)...")

        model_id = "stabilityai/stable-diffusion-3.5-large"
        try:
            torch.cuda.empty_cache()
            pipe = StableDiffusion3Pipeline.from_pretrained(
                model_id,
                cache_dir=MODEL_DIR,
                torch_dtype=torch.float16,
                use_safetensors=True,
                token=token
            ).to("cuda")

            print("Model downloaded and loaded.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")
    else:
        print("Model already loaded, skipping load.")

class GenerationRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_image(data: GenerationRequest):
    try:
        prompt = data.prompt
        image = pipe(prompt).images[0]

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return JSONResponse(content={"image_base64": img_str, "id": str(uuid.uuid4())})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

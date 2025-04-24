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
MODEL_DIR = "/runpod-volume/stable-diffusion-3.5"  # You can adjust this as needed

token = os.getenv("HF_TOKEN")

if not token:
    raise ValueError("Hugging Face token is missing. Please set it as an environment variable.")

pipe = None

# Set environment variable to prevent memory fragmentation
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"  # Use a smaller max split size to avoid fragmentation

@app.on_event("startup")
async def load_model():
    global pipe
    if pipe is None:  # Check if the model is already loaded
        print("Loading model...")  # This will log if model loading is triggered
        model_id = "stabilityai/stable-diffusion-3.5-large"

        # Clear CUDA memory before loading the model
        try:
            torch.cuda.empty_cache()
            pipe = StableDiffusion3Pipeline.from_pretrained(
                model_id,
                cache_dir=MODEL_DIR,  # Ensure this path is pointing to persistent storage
                torch_dtype=torch.float16,  # Use mixed precision (half-precision)
                use_safetensors=True,
                token=token
            ).to("cuda")
            print("Model loaded.")
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
        # Generate image using the preloaded model
        image = pipe(prompt).images[0]

        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return JSONResponse(content={"image_base64": img_str, "id": str(uuid.uuid4())})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

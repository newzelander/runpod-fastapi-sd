import os
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from diffusers import StableDiffusion3Pipeline
from fastapi.responses import JSONResponse
from io import BytesIO
from PIL import Image
import base64
import uuid

app = FastAPI()

# Get Hugging Face token from environment
token = os.getenv("HF_TOKEN")
if not token:
    raise ValueError("Hugging Face token is missing. Please set it as an environment variable.")

# Global model pipeline
pipe = None

@app.on_event("startup")
async def load_model():
    global pipe
    model_id = "stabilityai/stable-diffusion-3.5-large"
    pipe = StableDiffusion3Pipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        use_safetensors=True,
        use_auth_token=token  # Ensure token is used if model is gated/private
    ).to("cuda")

class GenerationRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate_image(data: GenerationRequest):
    prompt = data.prompt

    # Generate the image
    image = pipe(prompt).images[0]

    # Convert image to base64 string
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return JSONResponse(content={"image_base64": img_str, "id": str(uuid.uuid4())})

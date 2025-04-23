import torch
from fastapi import FastAPI
from pydantic import BaseModel
from diffusers import StableDiffusionPipeline
from fastapi.responses import JSONResponse
from io import BytesIO
from PIL import Image
import base64
import uuid

app = FastAPI()

# Preload the model during startup
model_id = "stabilityai/stable-diffusion-3.5"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    use_safetensors=True
).to("cuda")

class GenerationRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate_image(data: GenerationRequest):
    prompt = data.prompt

    image = pipe(prompt).images[0]

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return JSONResponse(content={"image_base64": img_str, "id": str(uuid.uuid4())})

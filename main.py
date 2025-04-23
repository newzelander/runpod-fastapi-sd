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

# Define global pipe variable to hold the preloaded model
pipe = None

@app.on_event("startup")
async def load_model():
    global pipe
    # Preload the model during FastAPI startup
    model_id = "stabilityai/stable-diffusion-3.5"
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        use_safetensors=True
    ).to("cuda")  # Ensures model is loaded onto the GPU

class GenerationRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate_image(data: GenerationRequest):
    prompt = data.prompt

    # Generate image using the preloaded model
    image = pipe(prompt).images[0]

    # Convert the image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return JSONResponse(content={"image_base64": img_str, "id": str(uuid.uuid4())})

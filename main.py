from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
import uuid
import base64
import os
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline
from io import BytesIO

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model globally once
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

# Limit concurrency to e.g. 4 simultaneous generations
executor = ThreadPoolExecutor(max_workers=4)

def generate_image(prompt: str, seed: int):
    generator = torch.Generator(device=pipe.device).manual_seed(seed)
    image = pipe(prompt, num_inference_steps=25, generator=generator).images[0]

    # Save image to bytes
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    # Save image file for serving
    filename = f"{uuid.uuid4()}.png"
    image_path = f"images/{filename}"
    os.makedirs("images", exist_ok=True)
    with open(image_path, "wb") as f:
        f.write(buffer.read())

    return f"https://yourdomain.com/images/{filename}"  # adjust this to your public URL

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    prompt = data.get("prompt")
    seed = data.get("seed", 42)

    loop = asyncio.get_event_loop()
    image_url = await loop.run_in_executor(executor, generate_image, prompt, seed)

    return {"status": "success", "image_url": image_url}

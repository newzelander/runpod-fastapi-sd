import os
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from diffusers import StableDiffusion3Pipeline
from transformers import CLIPTextModel, CLIPTokenizer  # Add the necessary imports for tokenizer and model
from fastapi.responses import JSONResponse
from io import BytesIO
from PIL import Image
import base64
import uuid

app = FastAPI()

# Fetch the Hugging Face token from the environment variable (with RUNPOD_SECRET_ prefix)
token = os.getenv("HF_TOKEN")  # This will retrieve the secret using the correct key

if not token:
    raise ValueError("Hugging Face token is missing. Please set it as an environment variable.")

# Define global pipe variable to hold the preloaded model
pipe = None

# Load the tokenizer (CLIPTokenizer) for StableDiffusion3Pipeline
tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch16")

@app.on_event("startup")
async def load_model():
    global pipe
    # Preload the model during FastAPI startup
    model_id = "stabilityai/stable-diffusion-3.5-large"
    
    # Initialize the Stable Diffusion pipeline with the tokenizer
    pipe = StableDiffusion3Pipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        use_safetensors=True,
        tokenizer=tokenizer  # Pass the tokenizer here
    ).to("cuda")  # Ensures model is loaded onto the GPU

class GenerationRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate_image(data: GenerationRequest):
    prompt = data.prompt

    # Tokenize the prompt using the tokenizer
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")

    # Generate image using the preloaded model
    image = pipe(prompt).images[0]

    # Convert the image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return JSONResponse(content={"image_base64": img_str, "id": str(uuid.uuid4())})

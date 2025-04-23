from fastapi import FastAPI
from pydantic import BaseModel
from diffusers import StableDiffusionPipeline
import torch
import uuid
import base64
from io import BytesIO
from fastapi.responses import JSONResponse

app = FastAPI()

# Load local model
print("Loading local Stable Diffusion model...")
model_path = "/app/models/sd3.5"
pipe = StableDiffusionPipeline.from_pretrained(model_path, torch_dtype=torch.float16)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
print("Model loaded successfully.")

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {"message": "Service is running"}

@app.post("/runsync")
async def generate_image(data: PromptRequest):
    try:
        print(f"Generating image for prompt: {data.prompt}")
        img_base64 = generate_image_from_prompt(data.prompt)
        return JSONResponse(content={"image_base64": img_base64})
    except Exception as e:
        print(f"Error occurred during image generation: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to generate image. Please try again."})

def generate_image_from_prompt(prompt: str) -> str:
    result = pipe(prompt, num_inference_steps=50, guidance_scale=7.5).images[0]
    img_byte_arr = BytesIO()
    result.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return base64.b64encode(img_byte_arr.read()).decode("utf-8")

# Local testing (optional)
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=3000)

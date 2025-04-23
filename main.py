import os
from fastapi import FastAPI
from pydantic import BaseModel
from huggingface_hub import InferenceClient
import uuid
import base64
from io import BytesIO
from fastapi.responses import JSONResponse

app = FastAPI()

# Fetch the Hugging Face token from the environment variable (with RUNPOD_SECRET_ prefix)
token = os.getenv("RUNPOD_SECRET_HF_TOKEN")  # This will retrieve the secret using the correct key

if not token:
    raise ValueError("Hugging Face token is missing. Please set it as an environment variable.")

model_id = "stabilityai/stable-diffusion-3.5-large"

print("Initializing InferenceClient...")
try:
    client = InferenceClient(token=token)
    print("InferenceClient initialized successfully.")
except Exception as e:
    print(f"Error initializing InferenceClient: {e}")

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

# ✅ This is the function your RunPod handler will import
def generate_image_from_prompt(prompt: str) -> str:
    result = client.text_to_image(
        model=model_id,
        prompt=prompt,
        num_inference_steps=50,
        guidance_scale=7.5
    )
    img_byte_arr = BytesIO()
    result.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return base64.b64encode(img_byte_arr.read()).decode("utf-8")

# Local testing (optional)
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=3000)

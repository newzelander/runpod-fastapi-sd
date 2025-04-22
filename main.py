from fastapi import FastAPI
from pydantic import BaseModel
from huggingface_hub import InferenceClient
from fastapi.responses import FileResponse
import uuid

app = FastAPI()

print("FastAPI app initialized")  # ✅ Helpful log for RunPod

token = "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"
model_id = "stabilityai/stable-diffusion-3.5-large"
client = InferenceClient(token=token)

class PromptRequest(BaseModel):
    prompt: str

# ✅ Health check endpoint for RunPod
@app.get("/")
async def root():
    return {"message": "Service is running"}

# ✅ Main image generation route
@app.post("/runsync")
async def generate_image(data: PromptRequest):
    print(f"Generating image for prompt: {data.prompt}")  # ✅ Debug log
    unique_filename = f"generated_{uuid.uuid4().hex}.png"
    result = client.text_to_image(
        model=model_id,
        prompt=data.prompt,
        num_inference_steps=50,
        guidance_scale=7.5
    )
    result.save(unique_filename)
    return FileResponse(unique_filename, media_type="image/png", filename=unique_filename)

# ✅ For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)

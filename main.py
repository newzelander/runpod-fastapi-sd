from fastapi import FastAPI
from pydantic import BaseModel
from huggingface_hub import InferenceClient
from fastapi.responses import FileResponse
import uuid

app = FastAPI()

token = "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"
model_id = "stabilityai/stable-diffusion-3.5-large"
client = InferenceClient(token=token)

class PromptRequest(BaseModel):
    prompt: str

@app.post("/run")
async def generate_image(data: PromptRequest):
    unique_filename = f"generated_{uuid.uuid4().hex}.png"
    result = client.text_to_image(
        model=model_id,
        prompt=data.prompt,
        num_inference_steps=50,
        guidance_scale=7.5
    )
    result.save(unique_filename)
    return FileResponse(unique_filename, media_type="image/png", filename=unique_filename)

# 👇 Add this block to make it work with exposed port 3000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)

from fastapi import FastAPI
from pydantic import BaseModel
from huggingface_hub import InferenceClient
import uuid
import base64
from io import BytesIO
from fastapi.responses import JSONResponse

app = FastAPI()

token = "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"
model_id = "stabilityai/stable-diffusion-3.5-large"
client = InferenceClient(token=token)

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {"message": "Service is running"}

@app.post("/runsync")
async def generate_image(data: PromptRequest):
    print(f"Generating image for prompt: {data.prompt}")

    # Generate the image
    result = client.text_to_image(
        model=model_id,
        prompt=data.prompt,
        num_inference_steps=50,
        guidance_scale=7.5
    )
    
    # Convert the image to base64
    img_byte_arr = BytesIO()
    result.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    
    img_base64 = base64.b64encode(img_byte_arr.read()).decode("utf-8")
    
    return JSONResponse(content={"image_base64": img_base64})

# Local testing (optional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)

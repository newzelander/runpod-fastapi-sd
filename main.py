from fastapi import FastAPI, Request 
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://spaceluma.webflow.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_image(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "").strip()
    negative_prompt = data.get("negative_prompt", "").strip()
    variation_id = data.get("index") or 0  # 👈 Add variation index from frontend

    if not prompt:
        return {"status": "error", "message": "No prompt provided."}

    # 👇 Add variation suffix to change image slightly
    varied_prompt = f"{prompt}, version {variation_id + 1}"

    base_url = "https://image.pollinations.ai/prompt/"
    prompt_encoded = requests.utils.quote(varied_prompt)
    url = f"{base_url}{prompt_encoded}?model=flux&nologo=true"

    if negative_prompt:
        neg_encoded = requests.utils.quote(negative_prompt)
        url += f"&negPrompt={neg_encoded}"

    try:
        return {
            "status": "success",
            "image_url": url
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "Image generation failed.",
            "error": str(e)
        }

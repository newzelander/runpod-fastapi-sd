from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# ✅ CORS setup: allow requests from your Webflow site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://spaceluma.webflow.io"],  # Update this if your domain changes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_image(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "").strip()
    negative_prompt = data.get("negative_prompt", "").strip()
    seed = data.get("seed")

    if not prompt:
        return {"status": "error", "message": "No prompt provided."}

    base_url = "https://image.pollinations.ai/prompt/"
    prompt_encoded = requests.utils.quote(prompt)
    url = f"{base_url}{prompt_encoded}?model=flux&nologo=true"

    if seed:
        url += f"&seed={seed}"
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

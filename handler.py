from fastapi import FastAPI, Request 
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# ✅ Correct CORS setup — must include protocol (https://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://spaceluma.webflow.io"],  # ✅ must include full URL
    allow_credentials=True,
    allow_methods=["*"],  # ✅ allow all standard methods like POST, GET, etc.
    allow_headers=["*"],  # ✅ allow all standard headers
)

@app.post("/generate")
async def generate_image(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "").strip()
    negative_prompt = data.get("negative_prompt", "").strip()

    if not prompt:
        return {"status": "error", "message": "No prompt provided."}

    base_url = "https://image.pollinations.ai/prompt/"
    prompt_encoded = requests.utils.quote(prompt)
    url = f"{base_url}{prompt_encoded}?model=flux&nologo=true"

    if negative_prompt:
        neg_encoded = requests.utils.quote(negative_prompt)
        url += f"&negPrompt={neg_encoded}"

    try:
        # ✅ Return the direct image URL (no base64)
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

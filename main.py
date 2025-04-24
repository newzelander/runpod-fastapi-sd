import os
from fastapi import FastAPI, HTTPException

app = FastAPI()

MODEL_ID = "stabilityai/stable-diffusion-3.5-large"
MODEL_DIR = f"/root/.cache/huggingface/hub/models--{MODEL_ID.replace('/', '--')}"

@app.get("/")
def read_root():
    return {"message": "FastAPI is running."}

@app.post("/")
def check_model_cache():
    if os.path.exists(MODEL_DIR):
        return {"status": "Model is cached."}
    else:
        raise HTTPException(status_code=404, detail="Model NOT found in cache.")

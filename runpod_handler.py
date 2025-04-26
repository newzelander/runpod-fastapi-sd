import os
import runpod

MODEL_PATH = "/runpod-volume/models/stable-diffusion-3.5-large"

def my_handler(event):
    if os.path.exists(MODEL_PATH):
        return {"status": "success", "message": "Model folder exists."}
    else:
        return {"status": "error", "message": "Model path not found."}

runpod.serverless.start({"handler": my_handler})

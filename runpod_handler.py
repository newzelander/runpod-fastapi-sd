import os
import runpod

def handler(event):
    model_path = "/runpod-volume/models/stable-diffusion-3.5"
    exists = os.path.exists(model_path)
    return {"status": "✅ Cached" if exists else "❌ Not found"}

runpod.serverless.start({"handler": handler})

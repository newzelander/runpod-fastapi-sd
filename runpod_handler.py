import os

def handler(event):
    model_path = "/workspace/models/stable-diffusion-3.5"
    
    if not os.path.exists(model_path):
        return {"error": "❌ Model not found. Please run preload_model.py again."}
    
    return {"message": "✅ Model is cached and ready."}

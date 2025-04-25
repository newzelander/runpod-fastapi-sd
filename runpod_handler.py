import runpod
from diffusers import StableDiffusion3Pipeline

# Preload model function to be called only once when the worker starts
def preload_model():
    try:
        # Cache the model once in the persistent volume
        StableDiffusion3Pipeline.from_pretrained(
            "stabilityai/stable-diffusion-3.5-large",
            cache_dir="/workspace/models/stable-diffusion-3.5"
        )
        print("Model pre-loaded successfully!")
        return {"status": "Model preloaded successfully"}
    except Exception as e:
        print(f"Error preloading model: {str(e)}")
        return {"error": str(e)}

# RunPod job handler
def handler(job):
    return preload_model()  # Only preload the model, nothing else

# Start the RunPod serverless worker with the defined handler
runpod.serverless.start({"handler": handler})

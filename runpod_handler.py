import runpod
from main import generate_image_endpoint
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
    except Exception as e:
        print(f"Error preloading model: {str(e)}")

# RunPod job handler
def handler(job):
    try:
        # Ensure the model is pre-loaded before generating the image
        preload_model()
        
        # Get the prompt from the incoming job and generate the image
        prompt = job["input"]["prompt"]
        return generate_image_endpoint(prompt)
    except Exception as e:
        return {"error": str(e)}

# Start the RunPod serverless worker with the defined handler
runpod.serverless.start({"handler": handler})

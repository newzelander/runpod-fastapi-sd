
import os
import runpod
import traceback
from diffusers import StableDiffusion3Pipeline

MODEL_PATH = "/runpod-volume/models/stable-diffusion-3.5-large"

def my_handler(event):
    try:
        if not os.path.exists(MODEL_PATH):
            return {"status": "error", "message": "Model path not found."}

        # Try to load the Stable Diffusion 3 Pipeline
        pipe = StableDiffusion3Pipeline.from_pretrained(
            MODEL_PATH,
            local_files_only=True,
            trust_remote_code=True,
            safety_checker=None,
            torch_dtype="auto"
        )

        return {"status": "success", "message": "Model loaded successfully, no missing or corrupt files."}

    except Exception as e:
        # Get the full error traceback
        error_trace = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Failed to load model: {str(e)}",
            "details": error_trace  # Full traceback will show which file caused the failure
        }

runpod.serverless.start({"handler": my_handler})

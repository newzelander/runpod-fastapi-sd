import runpod
import logging
import os
import shutil
from diffusers import DiffusionPipeline
import torch
from huggingface_hub import login

# Setup detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Check Hugging Face token
hf_token = os.environ.get("HF_TOKEN")
if hf_token:
    logger.info("HF_TOKEN is set.")
    login(hf_token)
else:
    logger.warning("HF_TOKEN not found in environment variables.")

# Check disk usage
total, used, free = shutil.disk_usage("/")
logger.info(f"Disk usage — Total: {total // (1024**2)}MB | Used: {used // (1024**2)}MB | Free: {free // (1024**2)}MB")

# Global model variable
pipe = None

# Initialization
def init():
    global pipe
    try:
        logger.info("Initializing Stable Diffusion 3.5 large model...")
        pipe = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-3.5-large",
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16"
        ).to("cuda")
        logger.info("Model successfully loaded and moved to GPU.")
    except Exception as e:
        logger.exception("Error during model initialization.")

init()

# Handler
def handler(job, context):
    logger.info(f"Received job: {job}")
    try:
        input_data = job.get("input", {})
        prompt = input_data.get("prompt", "A scenic mountain at sunrise")
        logger.debug(f"Prompt: {prompt}")

        logger.info("Starting inference...")
        image = pipe(prompt).images[0]
        output_path = "/tmp/generated_image.png"
        image.save(output_path)
        logger.info("Image generation complete.")

        return {"image_path": output_path}
    except Exception as e:
        logger.exception("Error during handler execution.")
        return {"error": str(e)}

# Start Runpod serverless worker
logger.info("Starting Runpod serverless handler...")
runpod.serverless.start({"handler": handler})

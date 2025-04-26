import os
import runpod
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def handler(event):
    # Log the incoming event for debugging purposes
    logger.info(f"Received event: {event}")
    
    # Check if required fields 'id' and 'input' are present in the event
    if 'id' not in event or 'input' not in event:
        logger.error("❌ Missing required fields: 'id' or 'input'")
        return {"status": "❌ Missing required fields: 'id' or 'input'"}
    
    model_path = "/runpod-volume/models/stable-diffusion-3.5-large"
    
    # Log the model path check
    logger.info(f"Checking model path: {model_path}")
    
    # Check if the model exists in the given path
    exists = os.path.exists(model_path)
    
    # Log the result of the check
    logger.info(f"Model exists: {exists}")
    
    # Respond based on whether the model is cached
    if exists:
        return {"status": "✅ Cached"}
    else:
        return {"status": "❌ Not found"}

# Start the RunPod serverless worker
runpod.serverless.start({"handler": handler})
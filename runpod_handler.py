import os
import runpod

def handler(event):
    # Log the incoming event for debugging purposes
    print(f"Received event: {event}")
    
    # Check if required fields 'id' and 'input' are present in the event
    if 'id' not in event or 'input' not in event:
        return {"status": "❌ Missing required fields: 'id' or 'input'"}
    
    model_path = "/runpod-volume/models/stable-diffusion-3.5"
    
    # Log the model path check
    print(f"Checking model path: {model_path}")
    
    # Check if the model exists in the given path
    exists = os.path.exists(model_path)
    
    # Log the result of the check
    print(f"Model exists: {exists}")
    
    # Respond based on whether the model is cached
    return {"status": "✅ Cached" if exists else "❌ Not found"}

runpod.serverless.start({"handler": handler})

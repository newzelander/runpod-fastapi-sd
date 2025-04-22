import runpod
from main import generate_image_from_prompt

# Define a simple handler for RunPod jobs
def handler(job):
    try:
        prompt = job["input"]["prompt"]
        # Using async method for image generation
        image_base64 = generate_image_from_prompt(prompt)
        return {"image_base64": image_base64}
    except Exception as e:
        print(f"Handler error: {e}")
        return {"error": str(e)}

# Start RunPod serverless
runpod.serverless.start({"handler": handler})

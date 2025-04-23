import runpod
from main import generate_image_from_prompt

def handler(job):
    try:
        prompt = job["input"]["prompt"]
        image_base64 = generate_image_from_prompt(prompt)
        return {"image_base64": image_base64}
    except Exception as e:
        print(f"Handler error: {e}")
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})

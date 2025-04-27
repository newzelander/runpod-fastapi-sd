import runpod
from main import generate_image
import time

def my_handler(event):
    prompt = event["input"]["prompt"]
    seed = event["input"].get("seed", None)

    start_time = time.time()
    filename = generate_image(prompt, seed)
    end_time = time.time()

    return {
        "output": {
            "image_url": f"https://{event['runpod']['endpoint']}/output/{filename}",
            "time_taken_seconds": round(end_time - start_time, 2)
        }
    }

runpod.serverless.start({"handler": my_handler})

from main import pipe
import base64
from io import BytesIO

def handler(event):
    prompt = event["input"]["prompt"]
    
    # Generate image using the preloaded model
    image = pipe(prompt).images[0]

    # Convert image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return {"image_base64": img_str}

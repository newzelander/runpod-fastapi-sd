import os
import torch
from diffusers import StableDiffusion3Pipeline
from datetime import datetime

# 🐛 Debugging: Check if model files exist
model_dir = "/runpod-volume/models/stable-diffusion-3.5-large"
print("📂 Contents of model directory:", os.listdir(model_dir))
print("📄 Does model_index.json exist?", os.path.exists(os.path.join(model_dir, "model_index.json")))

# Load model
pipe = StableDiffusion3Pipeline.from_pretrained(
    model_dir,
    torch_dtype=torch.float16
).to("cuda")

# Simple generate function
def generate_image(prompt, seed=None):
    if seed is not None:
        generator = torch.Generator("cuda").manual_seed(seed)
        image = pipe(prompt=prompt, generator=generator).images[0]
    else:
        image = pipe(prompt=prompt).images[0]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename = f"{timestamp}.png"
    output_path = f"/tmp/{filename}"

    image.save(output_path)
    return filename

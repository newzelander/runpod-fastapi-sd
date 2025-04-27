import torch
from diffusers import StableDiffusion3Pipeline
from datetime import datetime

# Load model
pipe = StableDiffusion3Pipeline.from_pretrained(
    "/runpod-volume/models/stable-diffusion-3.5-large",
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

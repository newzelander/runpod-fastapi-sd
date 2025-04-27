import os
import requests

# Define the model directory path
model_path = "/runpod-volume/models/stable-diffusion-3.5-large"
model_index_url = "https://huggingface.co/stabilityai/stable-diffusion-3.5-large/resolve/main/model_index.json"

# Ensure the model directory exists
if not os.path.exists(model_path):
    os.makedirs(model_path)

# Download the model_index.json
def download_model_index():
    try:
        print("⬇️ Downloading model_index.json...")
        response = requests.get(model_index_url)
        response.raise_for_status()  # Check for any errors

        model_index_path = os.path.join(model_path, "model_index.json")
        with open(model_index_path, "wb") as f:
            f.write(response.content)

        print(f"✅ model_index.json downloaded to {model_index_path}")

    except Exception as e:
        print(f"❌ Error downloading model_index.json: {str(e)}")

if __name__ == "__main__":
    download_model_index()

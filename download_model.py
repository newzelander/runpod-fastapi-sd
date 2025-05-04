import os
import shutil
import json
import psutil
from transformers import AutoModel

# Path to the persistent volume cache directory for Hugging Face model
CACHE_DIR = '/runpod-volume/huggingface-cache/stable-diffusion-3.5-large'
MAX_DISK_USAGE = 0.90  # Max disk usage threshold (90%)

# Function to check available disk space
def check_disk_space():
    disk = psutil.disk_usage('/')
    available_space = disk.free / disk.total  # Calculate available space percentage
    return available_space

# Function to delete cached model if disk quota exceeded
def delete_cached_model():
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
        print(f"Disk quota exceeded. Deleted model from {CACHE_DIR}.")
    else:
        print(f"No model found to delete at {CACHE_DIR}.")

# Function to download the model
def download_model():
    if check_disk_space() < MAX_DISK_USAGE:
        print(f"Not enough disk space. Available space: {check_disk_space() * 100:.2f}%")
        delete_cached_model()
        return "Disk quota exceeded. Model download cancelled."

    # Check if model is already downloaded
    if not os.path.exists(CACHE_DIR):
        print(f"Model not found in {CACHE_DIR}. Downloading...")
        # Download model
        model = AutoModel.from_pretrained('stabilityai/stable-diffusion-3.5-large', cache_dir=CACHE_DIR)
        print("Model downloaded successfully.")
    else:
        print(f"Model already exists in {CACHE_DIR}. Skipping download.")
    
    # After downloading, show remaining disk space
    available_space = check_disk_space() * 100
    print(f"Disk space remaining: {available_space:.2f}%")
    return f"Disk space remaining: {available_space:.2f}%"

# Function to process the request when "RunSync" button is pressed in RunPod UI
def process_runpod_request(json_input):
    try:
        request_data = json.loads(json_input)
        
        # You can check for certain input keys or conditions here if needed
        print(f"Received input: {request_data}")

        # Execute model download process
        return download_model()
    
    except Exception as e:
        print(f"Error processing request: {e}")
        return f"Error processing request: {e}"

# Main entry point (when RunSync button is pressed)
if __name__ == "__main__":
    # Example: Assuming you receive JSON input from a file or API
    json_input = '{"action": "download_model"}'  # Example input
    result = process_runpod_request(json_input)
    print(result)

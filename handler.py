import os
import shutil
import torch
import json
from huggingface_hub import snapshot_download, login
from diffusers import StableDiffusion3Pipeline

# Function to show all existing folders/paths including ~/.cache/huggingface/hub
def show_existing_paths():
    print("Existing folders and paths:")
    paths_to_check = [
        "/runpod-volume",  # Path where RunPod volume is stored
        os.path.expanduser("~/.cache/huggingface/hub")  # Hugging Face cache path
    ]

    for path in paths_to_check:
        if os.path.exists(path):
            print(f"Path found: {path}")
        else:
            print(f"Path not found: {path}")

# Function to clear contents inside the directories (keeping the directories intact)
def clear_directory_contents():
    print("Starting to clear directory contents...")
    paths_to_clear = [
        "/runpod-volume",  # Path where RunPod volume is stored
        os.path.expanduser("~/.cache/huggingface/hub")  # Hugging Face cache path
    ]

    for path in paths_to_clear:
        if os.path.exists(path):
            print(f"Clearing contents of {path}...")
            if os.path.isdir(path):
                # Delete all files and subdirectories inside the directory
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Recursively delete directories
                    else:
                        os.remove(item_path)  # Delete files
                print(f"Cleared contents of: {path}")
            else:
                os.remove(path)
                print(f"Deleted file: {path}")
        else:
            print(f"Path does not exist: {path}")

# Function to ensure Hugging Face does not download the model twice
def configure_hugging_face_cache():
    print("Configuring Hugging Face cache to /runpod-volume...")
    # Set the Hugging Face cache directory to the runpod-volume directory
    os.environ["HF_HUB_CACHE"] = "/runpod-volume"  # Use runpod-volume as the cache directory
    
    # Optionally, you can disable the default cache altogether
    # os.environ["HF_HUB_DISABLE_CACHE"] = "1"  # Uncomment to disable the default Hugging Face cache

# Function to preload and load the model
def preload():
    print("Preloading the model...")
    # Set the model directory based on cache or runpod-volume
    model_dir = "/runpod-volume"  # or specify your own model path

    try:
        # Load model into memory
        pipe = StableDiffusion3Pipeline.from_pretrained(
            model_dir,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            use_safetensors=True
        )
        
        # Move model to the appropriate device (GPU if available, otherwise CPU)
        pipe.to("cuda" if torch.cuda.is_available() else "cpu")
        print("Model loaded into memory successfully.")
        return pipe
    except Exception as e:
        print(f"Error while loading model: {e}")
        return None

# Function to process the JSON input and trigger the appropriate action
def process_input(json_input):
    print("Processing input:", json_input)
    
    # Extract the action from the input
    action = json_input.get('input', {}).get('action', '')
    
    if action == "preload_model":
        # Perform the preload_model action
        print("Action: preload_model")
        preload()
    else:
        print(f"Unknown action: {action}")

# Main function to run the operations
def main():
    print("Starting the main function...")

    # Here we simulate receiving the input JSON (in reality, you will pass this as input to the script)
    json_input = {
        "id": "job-id-003",
        "input": {
            "action": "preload_model"
        }
    }

    # Process the input JSON
    process_input(json_input)

# Ensure the script runs when triggered by RunPod UI
if __name__ == "__main__":
    main()

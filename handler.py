import os
import shutil
import logging
import subprocess
import time
import psutil
import runpod.serverless

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Constants for disk usage check
DISK_PATH = "/runpod-volume"  # The directory to check disk usage for
MAX_DISK_USAGE = 0.9  # Maximum allowed disk usage (90%)

def check_disk_usage():
    """Check the disk usage of the persistent volume"""
    disk_usage = psutil.disk_usage(DISK_PATH)
    used = disk_usage.used / (1024 * 1024 * 1024)  # Convert bytes to GB
    total = disk_usage.total / (1024 * 1024 * 1024)  # Convert bytes to GB
    free = disk_usage.free / (1024 * 1024 * 1024)  # Convert bytes to GB
    logging.info(f"Disk Usage: {used:.2f}GB used, {free:.2f}GB free, {total:.2f}GB total.")
    return used, free, total

def download_model(event):
    """Download the model and handle the event"""
    # Get model details from the event
    model_name = event.get("model", "stabilityai/stable-diffusion-3.5-large")
    logging.info(f"Starting download for model: {model_name}")
    
    # Log disk usage before download
    used_before, free_before, total_before = check_disk_usage()

    # Check if there is enough space for the download
    # Let's assume a model size of 10GB as an example (you should replace this with actual size estimation)
    model_size_estimate_gb = 10  # Replace with actual model size or calculate dynamically
    if free_before < model_size_estimate_gb:
        logging.error(f"Not enough space to download the model. {free_before}GB free, but {model_size_estimate_gb}GB needed.")
        return {"status": "failure", "message": "Not enough space to download the model."}

    # Simulate model download process (you will replace this with the actual download code)
    # Example: subprocess.run(f"wget {model_name}", shell=True)
    # We simulate a model download here by sleeping for 5 seconds
    logging.info(f"Simulating model download for {model_name}...")
    time.sleep(5)  # Simulate download time

    # Log disk usage after download
    used_after, free_after, total_after = check_disk_usage()

    # Check if disk space exceeded during download
    if used_after > MAX_DISK_USAGE * total_after:
        logging.error("Disk quota exceeded during model download.")
        return {"status": "failure", "message": "Disk quota exceeded during model download."}

    logging.info(f"Download complete for model: {model_name}")
    return {"status": "success", "message": "Model download complete"}

def handler(event):
    """Main handler function that processes the event"""
    try:
        logging.info(f"Received event: {event}")
        
        # Ensure event contains the necessary data
        if not event.get("model"):
            return {"status": "failure", "message": "Model name missing in event data"}
        
        # Call the download model function
        result = download_model(event)

        return result

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return {"status": "failure", "message": str(e)}

# Start the RunPod serverless worker with the handler function
runpod.serverless.start({"handler": handler})

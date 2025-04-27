import runpod
from download_json import download_model_index  # Assuming your script is in download_json.py

def my_handler(event):
    download_model_index()  # Call the function to download the model index
    return {
        "output": {
            "message": "model_index.json downloaded successfully"
        }
    }

runpod.serverless.start({"handler": my_handler})

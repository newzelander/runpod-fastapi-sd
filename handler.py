import runpod
import download_model

def handler(event):
    """Handles the runsync request to download the model."""
    # Call the download_model function
    result = download_model.download_model()
    
    if 'error' in result:
        return {"status": "error", "message": result['error']}
    
    return {
        "status": "success",
        "message": "Model downloaded successfully.",
        "model_path": result['model_path'],
        "disk_usage": result['disk_usage']
    }

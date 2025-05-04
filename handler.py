import subprocess
import runpod

def handler(event):
    # Execute the preload_model.py script as part of the serverless function
    result = subprocess.run(["python", "preload_model.py"], capture_output=True, text=True)
    return {
        "status": "completed",
        "stdout": result.stdout,
        "stderr": result.stderr
    }

# Use the runpod serverless.start to start the serverless function
runpod.serverless.start({"handler": handler})

import runpod
from main import app

# Add a handler if needed (you can customize the handler if required)
config = {
    "app": app,
    "handler": "runsync",  # Ensure a valid handler is provided, for example, the "runsync" route
}

# Start the serverless FastAPI app on RunPod
runpod.serverless.start(config)

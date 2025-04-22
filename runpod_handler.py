import runpod
from main import app

# Ensure the handler is the actual function, not just a string
config = {
    "app": app,
    "handler": app.get("/runsync"),  # Direct reference to the runsync route
}

# Start the serverless FastAPI app on RunPod
runpod.serverless.start(config)

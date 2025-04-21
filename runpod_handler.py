import runpod
from main import app

# This tells RunPod to serve the FastAPI app
runpod.serverless.start({
    "app": app
})

import runpod
from main import app

# Start the serverless FastAPI app on RunPod
runpod.serverless.start({
    "app": app
})

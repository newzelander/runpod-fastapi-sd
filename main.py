from runpod.serverless import start
from handler import handler

# Start the serverless handler and wait for the job trigger
start({"handler": handler})

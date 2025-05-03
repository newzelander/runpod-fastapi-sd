from runpod.serverless import start
from handler import handler

# Starts only when RunSync is triggered
start({"handler": handler})

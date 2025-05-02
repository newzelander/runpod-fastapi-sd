from runpod.serverless import start
from delete_volume import handler  # Import your function

start({"handler": handler})  # Register the handler function

from runpod.serverless import start
from preload_model import handler

start({"handler": handler})

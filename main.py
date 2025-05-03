from runpod.serverless import start
from handler import handler

start({"handler": handler})

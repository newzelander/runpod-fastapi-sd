FROM python:3.10-slim

WORKDIR /app

COPY runpod_handler.py .

# This Dockerfile is now ready to be called by RunPod Serverless.
# DO NOT include CMD unless it's handler-based service execution.

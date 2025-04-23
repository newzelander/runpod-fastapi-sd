#!/bin/bash

# Check that token exists
if [ -z "$HF_TOKEN" ]; then
  echo "❌ Error: Hugging Face token not found in environment variable HF_TOKEN."
  exit 1
fi

# Clone using the token at runtime
echo "🔐 Cloning model using Hugging Face token..."
git clone https://${HF_TOKEN}@huggingface.co/stabilityai/stable-diffusion-3.5-large /model

# Run your main app or service
echo "✅ Model cloned successfully. Starting app..."
exec bash

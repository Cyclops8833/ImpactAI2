#!/bin/bash
# Production startup script for backend

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Start the server
echo "Starting ImpactAI Backend..."
uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}
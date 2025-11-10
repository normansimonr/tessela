#!/bin/bash

# Start FastAPI in the background on port 8001
echo "Starting FastAPI backend on port 8001..."
uvicorn backend.src.api.main:app --host 0.0.0.0 --port 8001 &

# Start Streamlit in the foreground, binding to the PORT environment variable
# Cloud Run provides the PORT environment variable
echo "Starting Streamlit frontend on port ${PORT}..."
streamlit run frontend/src/app.py --server.port ${PORT} --server.address 0.0.0.0

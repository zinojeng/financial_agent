#!/bin/bash

# Get the PORT from environment variable, default to 8501
PORT=${PORT:-8501}

echo "Starting Streamlit on port $PORT..."

# Run streamlit with the correct port
streamlit run app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false
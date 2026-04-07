#!/bin/bash
# Bonsai Chat — Launch Script
set -e

source .venv/bin/activate 2>/dev/null || true
echo "Starting Bonsai Chat..."
python3 app.py

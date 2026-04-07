#!/bin/bash
# Bonsai Chat — Installation Script for Linux
set -e

echo "=== Installing Bonsai Chat ==="

# 1. Detect Hardware and install llama-cpp-python
# As per memory, we use precompiled wheels to avoid build issues.
if command -v nvidia-smi >/dev/null 2>&1; then
    echo "NVIDIA GPU detected. Installing llama-cpp-python with CUDA support..."
    pip install llama-cpp-python --only-binary llama-cpp-python --index-url https://abetlen.github.io/llama-cpp-python/whl/cu121 --extra-index-url https://pypi.org/simple
elif command -v vulkaninfo >/dev/null 2>&1; then
    echo "Vulkan detected. Installing llama-cpp-python with Vulkan support..."
    pip install llama-cpp-python --only-binary llama-cpp-python --index-url https://abetlen.github.io/llama-cpp-python/whl/vulkan --extra-index-url https://pypi.org/simple
else
    echo "No specialized hardware detected. Installing CPU-only llama-cpp-python..."
    pip install llama-cpp-python --only-binary llama-cpp-python --index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --extra-index-url https://pypi.org/simple
fi

# 2. Install other dependencies
echo "Installing other Python dependencies..."
pip install -r requirements.txt

echo "=== Installation Complete! ==="
echo "Run with: ./run.sh"

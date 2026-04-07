@echo off
setlocal
echo === Installing Bonsai Chat ===

:: Create virtual environment if it doesn't exist
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate

:: 1. Detect Hardware and install llama-cpp-python
:: As per memory, we use precompiled wheels to avoid build issues.
where nvidia-smi >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo NVIDIA GPU detected. Installing llama-cpp-python with CUDA support...
    pip install llama-cpp-python --only-binary llama-cpp-python --index-url https://abetlen.github.io/llama-cpp-python/whl/cu121 --extra-index-url https://pypi.org/simple || (
        echo CUDA wheel failed, falling back to CPU...
        pip install llama-cpp-python --only-binary llama-cpp-python --index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --extra-index-url https://pypi.org/simple
    )
) else (
    echo No specialized hardware detected. Installing CPU-only llama-cpp-python...
    pip install llama-cpp-python --only-binary llama-cpp-python --index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --extra-index-url https://pypi.org/simple
)

:: 2. Install other dependencies
echo Installing other Python dependencies...
pip install -r requirements.txt

echo === Installation Complete! ===
echo Run with: run.bat
endlocal
pause

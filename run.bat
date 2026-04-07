@echo off
setlocal
call .venv\Scripts\activate 2>nul
echo Starting Bonsai Chat...
python app.py
endlocal
pause

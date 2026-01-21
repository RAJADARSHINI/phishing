@echo off
REM Phishing Detection Backend Startup Script
REM This script ensures clean startup by killing existing processes on port 8000

echo ========================================
echo Phishing Detection Backend Startup
echo ========================================
echo.

REM Kill any existing process on port 8000
echo Checking for existing processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Found process %%a on port 8000, terminating...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Starting backend server...
echo.

REM Navigate to backend directory
cd /d "%~dp0"

REM Install dependencies
..\.venv\Scripts\python.exe -m pip install -r requirements.txt

REM Activate virtual environment and start server
..\.venv\Scripts\python.exe app.py

pause

@echo off
REM Quick start script for Phishing Detection Backend (Windows)

echo ==========================================
echo Phishing Detection Backend - Quick Start
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    exit /b 1
)

REM Create virtual environment (optional but recommended)
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set up data directory
echo Setting up data directory...
python setup_data.py

REM Train models
echo Training models...
python train_models.py

REM Start server
echo Starting API server...
echo Server will be available at http://localhost:8000
python app.py

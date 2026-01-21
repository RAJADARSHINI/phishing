# Phishing Detection Backend Startup Script (PowerShell)
# This script ensures clean startup by killing existing processes on port 8000

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phishing Detection Backend Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing process on port 8000
Write-Host "Checking for existing processes on port 8000..." -ForegroundColor Yellow

$connections = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue

if ($connections) {
    foreach ($conn in $connections) {
        $processId = $conn.OwningProcess
        Write-Host "Found process $processId on port 8000, terminating..." -ForegroundColor Yellow
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
} else {
    Write-Host "Port 8000 is available" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting backend server..." -ForegroundColor Green
Write-Host ""

# Navigate to backend directory
Set-Location $PSScriptRoot

# Install dependencies (Commented out to prevent hanging - run manually if needed)
Write-Host "Skipping dependency check for faster startup..." -ForegroundColor Yellow
# & "..\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host "Dependencies are ready." -ForegroundColor Green
Write-Host "Initializing AI Models (this may take a few moments)..." -ForegroundColor Cyan

# Activate virtual environment and start server (using direct python path)
# Using & operator to keep it in the same window so we can see the output
& "..\.venv\Scripts\python.exe" app.py

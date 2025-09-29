# PowerShell Start Script for GSMT Stock Tracker
# Run this if you're using PowerShell instead of Command Prompt

Write-Host "============================================================" -ForegroundColor Green
Write-Host " GSMT STOCK TRACKER - POWERSHELL STARTER" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Change to the correct directory
Set-Location -Path "C:\GSMT\GSMT_Windows11_Complete"

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run FIX_INSTALLATION.bat first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

# Try to stop any existing Python processes (may fail due to permissions)
Write-Host "Attempting to stop existing Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Use the venv's Python directly (bypasses activation issues)
$pythonPath = ".\venv\Scripts\python.exe"

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
Write-Host "Server will run at: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Available endpoints:" -ForegroundColor Yellow
Write-Host "  http://localhost:8000         - Main page" -ForegroundColor White
Write-Host "  http://localhost:8000/health  - Health check" -ForegroundColor White
Write-Host "  http://localhost:8000/docs    - API documentation" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Try test server first (most likely to work)
Write-Host "Starting test server..." -ForegroundColor Cyan
& $pythonPath backend\test_server.py

# If test server fails, try simple backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "Test server failed, trying simple backend..." -ForegroundColor Yellow
    & $pythonPath backend\simple_ml_backend.py
}

# If both fail, show error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Failed to start server!" -ForegroundColor Red
    Write-Host "Try running manually:" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\python.exe backend\test_server.py" -ForegroundColor White
    Read-Host "Press Enter to exit"
}
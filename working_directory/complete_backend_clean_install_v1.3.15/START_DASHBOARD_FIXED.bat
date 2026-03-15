@echo off
REM Regime Dashboard Startup Script for Windows
REM Handles .env encoding issues automatically

echo ==========================================
echo  Regime Intelligence Dashboard Launcher
echo  Version: v1.3.13
echo ==========================================
echo.

REM Check if .env file exists and has issues
if exist .env (
    echo Checking .env file...
    REM Backup existing .env if it has issues
    copy .env .env.backup >nul 2>&1
)

REM Create a clean .env file
echo Creating clean .env file...
(
echo # Flask Configuration
echo FLASK_SECRET_KEY=your-secure-secret-key-change-this-in-production
echo FLASK_ENV=development
echo FLASK_DEBUG=True
echo.
echo # Dashboard Settings
echo DASHBOARD_HOST=0.0.0.0
echo DASHBOARD_PORT=5002
echo.
echo # Regime Intelligence Settings
echo REGIME_WEIGHT=0.20
echo CONFIDENCE_THRESHOLD=0.30
echo ADAPTIVE_WEIGHTS=True
echo.
echo # Authentication ^(CHANGE THESE!^)
echo ADMIN_USERNAME=admin
echo ADMIN_PASSWORD=changeme123
echo.
echo # Logging
echo LOG_LEVEL=INFO
) > .env

echo .env file created successfully
echo.

REM Set environment variable to skip dotenv loading
set FLASK_SKIP_DOTENV=1

echo Starting Regime Dashboard...
echo.
echo Dashboard will be available at:
echo   http://localhost:5002
echo   http://127.0.0.1:5002
echo.
echo Press Ctrl+C to stop the dashboard
echo.

REM Start the dashboard
python regime_dashboard.py

pause

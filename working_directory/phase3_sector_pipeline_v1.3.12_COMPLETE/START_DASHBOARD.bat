@echo off
echo ════════════════════════════════════════════════════════════
echo   Phase 3 Paper Trading Dashboard
echo ════════════════════════════════════════════════════════════
echo.
echo Starting dashboard server...
echo.
echo ┌──────────────────────────────────────────────────────────┐
echo │  Open your browser to: http://localhost:8050             │
echo └──────────────────────────────────────────────────────────┘
echo.
echo Dashboard Features:
echo   • Live portfolio value and P/L
echo   • Open positions with real-time updates
echo   • Intraday alerts feed
echo   • Performance metrics
echo   • Trade history
echo   • Market sentiment gauge
echo   • Auto-refreshes every 5 seconds
echo.
echo Press Ctrl+C to stop the dashboard
echo ════════════════════════════════════════════════════════════
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if dash is installed
python -c "import dash" 2>nul
if errorlevel 1 (
    echo [WARNING] Dash not installed. Installing now...
    pip install dash plotly
    echo.
)

REM Start dashboard
echo Starting dashboard...
python dashboard.py

echo.
echo Dashboard stopped.
pause

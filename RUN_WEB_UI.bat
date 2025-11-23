@echo off
REM Event Risk Guard - Web UI Launcher
REM Start the web interface for monitoring models and logs

echo ================================================================================
echo EVENT RISK GUARD - WEB UI
echo ================================================================================
echo.
echo Starting web interface...
echo.
echo The web UI will be available at: http://localhost:5000
echo.
echo Features:
echo   - View trained LSTM models
echo   - Monitor pipeline logs
echo   - Check market regime status
echo   - Browse latest opportunities
echo.
echo Press Ctrl+C to stop the server
echo.

python web_ui.py

echo.
echo Web UI stopped.
pause

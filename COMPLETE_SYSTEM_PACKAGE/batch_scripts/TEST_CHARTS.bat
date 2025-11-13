@echo off
echo ===============================================
echo   Testing FinBERT Charts Component
echo ===============================================
echo.

:: Check if backend is running
curl -s http://localhost:5000/ >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Backend server is not running!
    echo.
    echo Please run one of these first:
    echo   - RUN_FINBERT_WITH_CHARTS.bat
    echo   - python app_finbert_ultimate.py
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Backend server is running at http://localhost:5000
echo.
echo Opening charts interface...
start "" "finbert_charts.html"

echo.
echo Charts opened in your default browser.
echo If charts don't load data, make sure the backend is running.
echo.
pause
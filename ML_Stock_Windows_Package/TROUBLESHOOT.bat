@echo off
REM ============================================================
REM ML STOCK PREDICTOR - TROUBLESHOOTING TOOL
REM ============================================================

title ML Stock Predictor - Troubleshooting
color 0E
cls

echo ============================================================
echo    ML STOCK PREDICTOR - TROUBLESHOOTING
echo ============================================================
echo.
echo This tool will help identify and fix common issues
echo.

REM Run diagnostic tool
echo Running diagnostics...
echo.
python diagnostics.py

echo.
echo ============================================================
echo    COMMON FIXES
echo ============================================================
echo.
echo 1. PORT 8000 IN USE:
echo    - Close any other applications using port 8000
echo    - Or run: netstat -ano ^| findstr :8000
echo    - Then: taskkill /F /PID [process_id]
echo.
echo 2. FIREWALL BLOCKING:
echo    - Allow Python through Windows Firewall
echo    - Run as Administrator if needed
echo.
echo 3. MISSING PACKAGES:
echo    - Run: pip install -r requirements.txt
echo.
echo 4. BROWSER ISSUES:
echo    - Try different browser (Chrome, Edge, Firefox)
echo    - Clear browser cache
echo    - Disable browser extensions temporarily
echo.
echo ============================================================
echo.
pause
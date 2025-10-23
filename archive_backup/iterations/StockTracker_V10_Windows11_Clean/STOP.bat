@echo off
echo ========================================
echo Stopping StockTracker Services
echo ========================================
echo.

echo Terminating all Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul

echo.
echo All services stopped.
echo.
pause
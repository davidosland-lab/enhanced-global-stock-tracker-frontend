@echo off
echo =====================================
echo ML Stock Prediction System - Diagnostics
echo =====================================
echo.

echo Running diagnostic checks...
python diagnostic.py

echo.
echo =====================================
echo Diagnostic complete!
echo.
echo If all checks passed:
echo - Run 3_start_server.bat to start the system
echo.
echo If there were errors:
echo - Fix the issues mentioned above
echo - Run this test again
echo =====================================
pause
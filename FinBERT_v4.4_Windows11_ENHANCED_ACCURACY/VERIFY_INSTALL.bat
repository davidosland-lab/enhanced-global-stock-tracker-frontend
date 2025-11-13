@echo off
echo ================================================================================
echo   FinBERT v4.4 - Installation Verification
echo ================================================================================
echo.
echo This script will verify your installation is complete and ready to use.
echo.
pause

echo.
echo Step 1: Running Python diagnostic tool...
echo.
python diagnose_environment.py

echo.
echo ================================================================================
echo   Verification Complete
echo ================================================================================
echo.
echo Did the diagnostic show "ALL CHECKS PASSED"?
echo.
echo   YES - You can start the server with: START_FINBERT.bat
echo   NO  - Run the fix script: FIX_FLASK_CORS.bat
echo.
pause

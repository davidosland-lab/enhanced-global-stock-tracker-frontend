@echo off
:: Opens Command Prompt in the GSMT directory
:: Use this to run commands manually

cd /d "C:\GSMT\GSMT_Windows11_Complete"
echo ============================================================
echo  GSMT COMMAND PROMPT
echo ============================================================
echo.
echo You are now in: C:\GSMT\GSMT_Windows11_Complete
echo.
echo Quick commands you can run:
echo.
echo   venv\Scripts\python.exe backend\test_server.py
echo     (Starts test server)
echo.
echo   venv\Scripts\python.exe backend\simple_ml_backend.py
echo     (Starts main server)
echo.
echo   venv\Scripts\activate
echo     (Activates virtual environment)
echo.
echo ============================================================
echo.
cmd /k
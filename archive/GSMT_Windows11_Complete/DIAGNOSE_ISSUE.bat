@echo off
:: Diagnostic script to identify why endpoints aren't working

color 0E
cls

echo ============================================================
echo  GSMT DIAGNOSTIC TOOL
echo  Finding why endpoints return "not found"
echo ============================================================
echo.

cd /d "C:\GSMT\GSMT_Windows11_Complete"

:: Activate venv
call venv\Scripts\activate.bat

echo Step 1: Testing Python and FastAPI installation
echo ============================================
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"
python -c "import uvicorn; print('Uvicorn installed: OK')"
echo.

echo Step 2: Testing backend imports
echo ============================================
python TEST_BACKEND.py
echo.

echo Step 3: Checking what's currently running
echo ============================================
echo Checking port 8000...
netstat -an | findstr :8000
echo.

echo Step 4: Trying test server
echo ============================================
echo Starting a minimal test server...
echo This should definitely work. If it does, the issue is with the main backend.
echo.
echo After the test server starts:
echo   1. Open http://localhost:8000 
echo   2. Try http://localhost:8000/health
echo   3. If these work, press Ctrl+C to stop
echo   4. Then we'll fix the main backend
echo.
pause

:: Start test server
python backend\test_server.py
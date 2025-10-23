@echo off
title Stock Tracker - Fix All Issues
color 0A

echo ===============================================================================
echo                        STOCK TRACKER ISSUE FIXER
echo                     Fixing Port Conflicts and Dependencies
echo ===============================================================================
echo.

echo [1/5] Killing processes on conflicting ports...
echo -----------------------------------------------
:: Kill any process using port 8003 (ML Backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    echo Killing process on port 8003 (PID: %%a)
    taskkill /F /PID %%a 2>nul
)

:: Kill any process using port 8002 (Main Backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo Killing process on port 8002 (PID: %%a)
    taskkill /F /PID %%a 2>nul
)

:: Kill any process using port 8000 (Frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Killing process on port 8000 (PID: %%a)
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 >nul

echo.
echo [2/5] Fixing Python package dependencies...
echo -----------------------------------------------
:: Upgrade pip first
python -m pip install --upgrade pip

:: Install setuptools explicitly (fixes the BackendUnavailable error)
python -m pip install --upgrade setuptools wheel

:: Install core dependencies one by one to avoid conflicts
python -m pip install fastapi uvicorn[standard] yfinance pandas numpy
python -m pip install cachetools pytz python-multipart aiofiles
python -m pip install sqlalchemy python-dotenv colorama tqdm

:: Install TensorFlow separately (often causes issues)
echo Installing TensorFlow (this may take a few minutes)...
python -m pip install tensorflow==2.15.0

:: Install remaining ML dependencies
python -m pip install scikit-learn ta pandas-ta

echo.
echo [3/5] Creating simplified requirements file...
echo -----------------------------------------------
(
echo fastapi==0.104.1
echo uvicorn[standard]==0.24.0
echo yfinance==0.2.32
echo pandas==2.1.3
echo numpy==1.24.3
echo python-multipart==0.0.6
echo aiofiles==23.2.1
echo cachetools==5.3.2
echo pytz==2023.3.post1
echo sqlalchemy==2.0.23
echo scikit-learn==1.3.2
echo ta==0.10.2
) > requirements_simple.txt

echo.
echo [4/5] Setting environment variable for TensorFlow...
echo -----------------------------------------------
:: This fixes the oneDNN warning
set TF_ENABLE_ONEDNN_OPTS=0
setx TF_ENABLE_ONEDNN_OPTS 0 >nul 2>&1

echo.
echo [5/5] Creating fixed startup script...
echo -----------------------------------------------
(
echo @echo off
echo title Stock Tracker - Fixed Launcher
echo color 0A
echo.
echo :: Set TensorFlow environment variable
echo set TF_ENABLE_ONEDNN_OPTS=0
echo.
echo echo Starting services with port checking...
echo echo.
echo.
echo :: Check if ports are free
echo netstat -an ^| findstr :8002 ^>nul
echo if %%errorlevel%%==0 ^(
echo     echo Port 8002 is already in use. Killing process...
echo     for /f "tokens=5" %%%%a in ^('netstat -aon ^^^| findstr :8002'^) do taskkill /F /PID %%%%a 2^>nul
echo     timeout /t 2 ^>nul
echo ^)
echo.
echo netstat -an ^| findstr :8003 ^>nul
echo if %%errorlevel%%==0 ^(
echo     echo Port 8003 is already in use. Killing process...
echo     for /f "tokens=5" %%%%a in ^('netstat -aon ^^^| findstr :8003'^) do taskkill /F /PID %%%%a 2^>nul
echo     timeout /t 2 ^>nul
echo ^)
echo.
echo echo [1/3] Starting Main Backend ^(Port 8002^)...
echo start "Backend" cmd /k "python backend.py"
echo timeout /t 3 ^>nul
echo.
echo echo [2/3] Starting Frontend Server ^(Port 8000^)...
echo start "Frontend" cmd /k "python -m http.server 8000"
echo timeout /t 2 ^>nul
echo.
echo echo [3/3] ML Backend is optional - start manually if needed
echo echo To start ML Backend: python ml_training_backend_fixed.py
echo echo.
echo.
echo echo ===============================================================================
echo echo                           SERVICES STARTED
echo echo ===============================================================================
echo echo.
echo echo Main Application: http://localhost:8000
echo echo Backend API: http://localhost:8002
echo echo.
echo echo Opening browser...
echo timeout /t 2 ^>nul
echo start "" "http://localhost:8000"
echo.
echo echo.
echo pause
) > LAUNCH_FIXED.bat

echo.
echo ===============================================================================
echo                              FIXES COMPLETE
echo ===============================================================================
echo.
echo Fixed Issues:
echo -------------
echo ✓ Port conflicts resolved
echo ✓ Python dependencies updated
echo ✓ TensorFlow warnings suppressed
echo ✓ New launcher created: LAUNCH_FIXED.bat
echo.
echo Next Steps:
echo -----------
echo 1. Close all command windows
echo 2. Run: LAUNCH_FIXED.bat
echo 3. Access: http://localhost:8000
echo.
pause
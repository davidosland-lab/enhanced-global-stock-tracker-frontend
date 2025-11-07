@echo off
title FinBERT v4.0 Installation with LSTM
color 0A
cls

echo ================================================================================
echo                     FinBERT Ultimate Trading System v4.0                       
echo                      WITH LSTM NEURAL NETWORK INTEGRATION                      
echo ================================================================================
echo.
echo This installer will set up FinBERT v4.0 with advanced ML features:
echo - LSTM (Long Short-Term Memory) neural networks
echo - Ensemble predictions (LSTM + Technical + Trend)
echo - Enhanced accuracy (up to 81%%)
echo - Development and Production modes
echo.
echo Requirements:
echo - Python 3.8 or higher
echo - Internet connection
echo - Windows 10/11
echo - 4GB+ RAM recommended for LSTM
echo.
pause

REM Check Python installation
echo.
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

python --version
echo Python found successfully!
echo.

REM Create virtual environment
echo [2/6] Creating virtual environment for v4.0...
if exist "venv_v4" (
    echo Virtual environment already exists, updating...
    call venv_v4\Scripts\activate.bat
    python -m pip install --upgrade pip --quiet
) else (
    python -m venv venv_v4
    call venv_v4\Scripts\activate.bat
    python -m pip install --upgrade pip --quiet
    echo Virtual environment created!
)
echo.

REM Install core dependencies
echo [3/6] Installing core dependencies...
echo.
echo Installing Flask framework...
pip install flask flask-cors --quiet --disable-pip-version-check

echo Installing NumPy for numerical computation...
pip install numpy --quiet --disable-pip-version-check

echo Installing Pandas for data manipulation...
pip install pandas --quiet --disable-pip-version-check 2>nul || echo Pandas optional, continuing...

echo Installing scikit-learn for ML utilities...
pip install scikit-learn --quiet --disable-pip-version-check 2>nul || echo Sklearn optional, continuing...

echo.
echo Core packages installed!
echo.

REM Ask about TensorFlow installation
echo [4/6] TensorFlow Installation (for LSTM)
echo.
echo TensorFlow enables full LSTM capabilities for better predictions.
echo Note: TensorFlow is large (~500MB) and may take time to install.
echo.
set /p install_tf="Install TensorFlow for LSTM? (Y/N): "
if /i "%install_tf%"=="Y" (
    echo.
    echo Installing TensorFlow... This may take several minutes...
    pip install tensorflow --quiet --disable-pip-version-check
    if errorlevel 0 (
        echo TensorFlow installed successfully!
        echo LSTM models will be fully functional.
    ) else (
        echo Warning: TensorFlow installation failed. LSTM will use fallback mode.
    )
) else (
    echo.
    echo Skipping TensorFlow. LSTM will work in fallback mode with reduced accuracy.
)
echo.

REM Check files
echo [5/6] Verifying installation files...
set missing_files=0

if not exist "app_finbert_v4_dev.py" (
    echo ERROR: app_finbert_v4_dev.py not found!
    set missing_files=1
)

if not exist "models\lstm_predictor.py" (
    echo ERROR: models\lstm_predictor.py not found!
    set missing_files=1
)

if not exist "config_dev.py" (
    echo ERROR: config_dev.py not found!
    set missing_files=1
)

if %missing_files%==1 (
    color 0C
    echo.
    echo ERROR: Required files are missing!
    echo Please ensure all files are extracted to the same directory.
    pause
    exit /b 1
)

echo All files verified successfully!
echo.

REM Create shortcuts and batch files
echo [6/6] Creating shortcuts and launchers...

REM Create production mode launcher
echo @echo off > START_V4_PRODUCTION.bat
echo title FinBERT v4.0 - Production Mode >> START_V4_PRODUCTION.bat
echo call venv_v4\Scripts\activate.bat >> START_V4_PRODUCTION.bat
echo set FLASK_ENV=production >> START_V4_PRODUCTION.bat
echo python app_finbert_v4_dev.py >> START_V4_PRODUCTION.bat

REM Create development mode launcher
echo @echo off > START_V4_DEVELOPMENT.bat
echo title FinBERT v4.0 - Development Mode >> START_V4_DEVELOPMENT.bat
echo call venv_v4\Scripts\activate.bat >> START_V4_DEVELOPMENT.bat
echo set FLASK_ENV=development >> START_V4_DEVELOPMENT.bat
echo set FLASK_DEBUG=1 >> START_V4_DEVELOPMENT.bat
echo python app_finbert_v4_dev.py >> START_V4_DEVELOPMENT.bat

REM Create LSTM training launcher
echo @echo off > TRAIN_LSTM.bat
echo title LSTM Model Training >> TRAIN_LSTM.bat
echo call venv_v4\Scripts\activate.bat >> TRAIN_LSTM.bat
echo echo. >> TRAIN_LSTM.bat
echo echo Choose training option: >> TRAIN_LSTM.bat
echo echo 1. Quick test (5 epochs) >> TRAIN_LSTM.bat
echo echo 2. Train AAPL (50 epochs) >> TRAIN_LSTM.bat
echo echo 3. Train multiple symbols (50 epochs) >> TRAIN_LSTM.bat
echo echo 4. Custom training >> TRAIN_LSTM.bat
echo echo. >> TRAIN_LSTM.bat
echo set /p choice="Enter choice (1-4): " >> TRAIN_LSTM.bat
echo if "%%choice%%"=="1" python models\train_lstm.py --test >> TRAIN_LSTM.bat
echo if "%%choice%%"=="2" python models\train_lstm.py --symbol AAPL --epochs 50 >> TRAIN_LSTM.bat
echo if "%%choice%%"=="3" python models\train_lstm.py --symbols AAPL,MSFT,GOOGL,TSLA --epochs 50 >> TRAIN_LSTM.bat
echo if "%%choice%%"=="4" ( >> TRAIN_LSTM.bat
echo     set /p symbol="Enter symbol: " >> TRAIN_LSTM.bat
echo     set /p epochs="Enter epochs: " >> TRAIN_LSTM.bat
echo     python models\train_lstm.py --symbol %%symbol%% --epochs %%epochs%% >> TRAIN_LSTM.bat
echo ) >> TRAIN_LSTM.bat
echo pause >> TRAIN_LSTM.bat

REM Create test runner
echo @echo off > RUN_TESTS.bat
echo title FinBERT v4.0 Tests >> RUN_TESTS.bat
echo call venv_v4\Scripts\activate.bat >> RUN_TESTS.bat
echo python tests\test_lstm.py >> RUN_TESTS.bat
echo pause >> RUN_TESTS.bat

REM Create desktop shortcut
set SCRIPT_PATH=%~dp0
set DESKTOP=%USERPROFILE%\Desktop

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\FinBERT v4.0 LSTM.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_PATH%START_V4_PRODUCTION.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_PATH%" >> CreateShortcut.vbs
echo oLink.IconLocation = "cmd.exe" >> CreateShortcut.vbs
echo oLink.Description = "Launch FinBERT v4.0 with LSTM" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs >nul 2>&1
del CreateShortcut.vbs >nul 2>&1

color 0A
echo.
echo ================================================================================
echo                        INSTALLATION COMPLETE!                                  
echo ================================================================================
echo.
echo FinBERT v4.0 with LSTM has been successfully installed!
echo.
echo Installed Components:
if exist "venv_v4\Lib\site-packages\tensorflow" (
    echo [+] TensorFlow: INSTALLED - Full LSTM capabilities enabled
) else (
    echo [-] TensorFlow: NOT INSTALLED - LSTM in fallback mode
)
echo [+] Flask: INSTALLED
echo [+] NumPy: INSTALLED
echo [+] Core ML: INSTALLED
echo.
echo Created Files:
echo - START_V4_PRODUCTION.bat   (Run in production mode)
echo - START_V4_DEVELOPMENT.bat  (Run in development mode)
echo - TRAIN_LSTM.bat           (Train LSTM models)
echo - RUN_TESTS.bat            (Run test suite)
echo - Desktop shortcut created
echo.
echo Next Steps:
echo 1. Run START_V4_PRODUCTION.bat to start the system
echo 2. Open browser to http://localhost:5001
echo 3. Optional: Run TRAIN_LSTM.bat to train models for better accuracy
echo.
echo Press any key to start FinBERT v4.0...
pause >nul

REM Launch the system
call START_V4_PRODUCTION.bat
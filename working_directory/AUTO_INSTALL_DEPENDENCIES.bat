@echo off
REM ============================================================================
REM AUTO DEPENDENCY INSTALLER - v1.3.15.58
REM ============================================================================
REM Automatically checks and installs missing dependencies at startup
REM This ensures LSTM neural networks work without manual intervention
REM ============================================================================

echo.
echo ============================================================================
echo   AUTO DEPENDENCY INSTALLER - Trading System v1.3.15.58
echo ============================================================================
echo.
echo Checking and installing required dependencies...
echo.

REM Detect if we're in a virtual environment
IF DEFINED VIRTUAL_ENV (
    echo [INFO] Virtual environment detected: %VIRTUAL_ENV%
    set PIP_CMD=pip
) ELSE (
    IF EXIST "venv\Scripts\pip.exe" (
        echo [INFO] Virtual environment found at .\venv
        set PIP_CMD=venv\Scripts\pip
    ) ELSE (
        echo [INFO] Using system Python
        set PIP_CMD=pip
    )
)

echo.
echo ============================================================================
echo   DEPENDENCY CHECK
echo ============================================================================
echo.

REM Check and install Keras
echo [1/4] Checking Keras...
%PIP_CMD% show keras >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] Keras not found - installing...
    %PIP_CMD% install keras --quiet
    IF ERRORLEVEL 1 (
        echo [ERROR] Failed to install Keras
        goto :error
    )
    echo [OK] Keras installed
) ELSE (
    echo [OK] Keras already installed
)

REM Check and install PyTorch
echo [2/4] Checking PyTorch...
%PIP_CMD% show torch >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] PyTorch not found - installing (~2GB, may take 2-5 minutes)...
    %PIP_CMD% install torch --index-url https://download.pytorch.org/whl/cpu --quiet
    IF ERRORLEVEL 1 (
        echo [ERROR] Failed to install PyTorch
        goto :error
    )
    echo [OK] PyTorch installed
) ELSE (
    echo [OK] PyTorch already installed
)

REM Check and install scikit-learn
echo [3/4] Checking scikit-learn...
%PIP_CMD% show scikit-learn >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] scikit-learn not found - installing...
    %PIP_CMD% install scikit-learn --quiet
    IF ERRORLEVEL 1 (
        echo [ERROR] Failed to install scikit-learn
        goto :error
    )
    echo [OK] scikit-learn installed
) ELSE (
    echo [OK] scikit-learn already installed
)

REM Set KERAS_BACKEND environment variable
echo [4/4] Checking KERAS_BACKEND environment variable...
IF "%KERAS_BACKEND%"=="torch" (
    echo [OK] KERAS_BACKEND already set to 'torch'
) ELSE (
    echo [*] Setting KERAS_BACKEND=torch...
    set KERAS_BACKEND=torch
    setx KERAS_BACKEND torch >nul 2>&1
    IF ERRORLEVEL 1 (
        echo [WARN] Could not set KERAS_BACKEND permanently
        echo [INFO] Set for current session only
    ) ELSE (
        echo [OK] KERAS_BACKEND set permanently
    )
)

echo.
echo ============================================================================
echo   VERIFICATION
echo ============================================================================
echo.

REM Verify installation
python -c "import os; os.environ['KERAS_BACKEND']='torch'; import keras; import torch; from sklearn.preprocessing import MinMaxScaler; print('[OK] All dependencies verified!'); print('    Keras:', keras.__version__); print('    PyTorch:', torch.__version__)" 2>nul
IF ERRORLEVEL 1 (
    echo [WARN] Verification failed - dependencies may need terminal restart
    echo [INFO] If you see errors, close this terminal and open a new one
) ELSE (
    echo.
    echo [SUCCESS] All LSTM dependencies are ready!
)

echo.
echo ============================================================================
echo   DEPENDENCY CHECK COMPLETE
echo ============================================================================
echo.
exit /b 0

:error
echo.
echo ============================================================================
echo   ERROR: Dependency installation failed
echo ============================================================================
echo.
echo Troubleshooting:
echo   1. Check internet connection
echo   2. Ensure you have write permissions
echo   3. Try running as Administrator
echo   4. Check if antivirus is blocking pip
echo.
exit /b 1

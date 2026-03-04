@echo off
title LSTM Model Training
call venv_v4\Scripts\activate.bat
echo.
echo ================================================================================
echo                         LSTM MODEL TRAINING
echo ================================================================================
echo.
echo Choose training option:
echo 1. Quick test (5 epochs)
echo 2. Train AAPL (50 epochs)
echo 3. Train multiple symbols (50 epochs)
echo 4. Custom training
echo 5. Train Australian stocks (ASX)
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    python models\train_lstm.py --test
    goto end
)

if "%choice%"=="2" (
    python models\train_lstm.py --symbol AAPL --epochs 50
    goto end
)

if "%choice%"=="3" (
    python models\train_lstm.py --symbols AAPL,MSFT,GOOGL,TSLA --epochs 50
    goto end
)

if "%choice%"=="4" (
    set /p symbol="Enter symbol (e.g., AAPL, MSFT): "
    set /p epochs="Enter number of epochs: "
    echo Training %symbol% for %epochs% epochs...
    python models\train_lstm.py --symbol %symbol% --epochs %epochs%
    goto end
)

if "%choice%"=="5" (
    echo.
    echo Australian Stock Training
    echo -------------------------
    echo Common ASX symbols:
    echo   CBA.AX  - Commonwealth Bank
    echo   BHP.AX  - BHP Group
    echo   CSL.AX  - CSL Limited
    echo   WBC.AX  - Westpac
    echo   ANZ.AX  - ANZ Bank
    echo   NAB.AX  - National Australia Bank
    echo   WES.AX  - Wesfarmers
    echo   MQG.AX  - Macquarie Group
    echo   TLS.AX  - Telstra
    echo   WOW.AX  - Woolworths
    echo.
    echo Enter ASX symbols WITH .AX suffix!
    set /p asx_symbols="Enter symbol(s) separated by comma (e.g., CBA.AX,BHP.AX): "
    set /p epochs="Enter number of epochs (default 50): "
    if "%epochs%"=="" set epochs=50
    
    echo Training Australian stocks: %asx_symbols%
    
    REM Check if multiple symbols or single
    echo %asx_symbols% | find "," >nul
    if errorlevel 1 (
        REM Single symbol
        python models\train_lstm.py --symbol %asx_symbols% --epochs %epochs%
    ) else (
        REM Multiple symbols
        python models\train_lstm.py --symbols %asx_symbols% --epochs %epochs%
    )
    goto end
)

echo Invalid choice!
goto end

:end
echo.
pause
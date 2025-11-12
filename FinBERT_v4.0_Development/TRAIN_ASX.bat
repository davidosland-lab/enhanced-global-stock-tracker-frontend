@echo off
title Train Australian (ASX) Stocks - LSTM
color 0B
cls

echo ================================================================================
echo                    LSTM TRAINING FOR AUSTRALIAN STOCKS (ASX)
echo ================================================================================
echo.
echo IMPORTANT: Use .AX suffix for all Australian stocks!
echo Examples: CBA.AX, BHP.AX, WBC.AX, ANZ.AX
echo.

call venv_v4\Scripts\activate.bat 2>nul

echo Choose training option:
echo.
echo 1. Train single stock (e.g., CBA.AX)
echo 2. Train Big 4 Banks (CBA, WBC, ANZ, NAB)
echo 3. Train Top 10 ASX stocks
echo 4. Train Mining stocks (BHP, RIO, FMG)
echo 5. Custom multiple stocks
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Common ASX Symbols:
    echo   CBA.AX - Commonwealth Bank
    echo   BHP.AX - BHP Group
    echo   CSL.AX - CSL Limited
    echo   WBC.AX - Westpac
    echo   ANZ.AX - ANZ Bank
    echo.
    set /p symbol="Enter ASX symbol WITH .AX (e.g., CBA.AX): "
    set /p epochs="Enter epochs (default 50): "
    if "%epochs%"=="" set epochs=50
    
    echo.
    echo Training %symbol% for %epochs% epochs...
    python train_australian_stocks.py --symbol %symbol% --epochs %epochs%
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Training Big 4 Australian Banks...
    echo - CBA.AX (Commonwealth Bank)
    echo - WBC.AX (Westpac)
    echo - ANZ.AX (ANZ Bank)
    echo - NAB.AX (National Australia Bank)
    echo.
    python train_australian_stocks.py --top4banks --epochs 50
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Training Top 10 ASX Stocks...
    python train_australian_stocks.py --top10 --epochs 50
    goto end
)

if "%choice%"=="4" (
    echo.
    echo Training Mining Stocks...
    echo - BHP.AX (BHP Group)
    echo - RIO.AX (Rio Tinto)
    echo - FMG.AX (Fortescue)
    echo - NCM.AX (Newcrest)
    echo - STO.AX (Santos)
    echo.
    python train_australian_stocks.py --miners --epochs 50
    goto end
)

if "%choice%"=="5" (
    echo.
    echo Enter multiple ASX symbols separated by commas.
    echo Example: CBA.AX,BHP.AX,CSL.AX
    echo.
    set /p symbols="Enter symbols: "
    set /p epochs="Enter epochs (default 50): "
    if "%epochs%"=="" set epochs=50
    
    echo.
    echo Training: %symbols%
    python train_australian_stocks.py --symbols %symbols% --epochs %epochs%
    goto end
)

echo Invalid choice!

:end
echo.
echo ================================================================================
echo Press any key to exit...
pause >nul
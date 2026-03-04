@echo off
REM US Market Pipeline Runner - Windows Launcher
REM NYSE/NASDAQ Trading Automation

echo ========================================
echo   US Market Pipeline Runner v1.3.11
echo   NYSE/NASDAQ Trading Automation
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo Select an option:
echo.
echo [1] US Tech Giants (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, AMD)
echo [2] US Blue Chips (AAPL, MSFT, JPM, JNJ, WMT, PG, UNH, V)
echo [3] FAANG (META, AAPL, AMZN, NFLX, GOOGL)
echo [4] Magnificent 7 (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA)
echo [5] US Financials (JPM, BAC, WFC, GS, MS, C, USB, PNC)
echo [6] US Growth (TSLA, NVDA, AMD, PLTR, SQ, COIN, SNOW, NET)
echo [7] Custom symbols
echo [8] List all presets
echo.
set /p CHOICE="Enter choice (1-8): "

if "%CHOICE%"=="1" set PRESET=US Tech Giants
if "%CHOICE%"=="2" set PRESET=US Blue Chips
if "%CHOICE%"=="3" set PRESET=FAANG
if "%CHOICE%"=="4" set PRESET=Magnificent 7
if "%CHOICE%"=="5" set PRESET=US Financials
if "%CHOICE%"=="6" set PRESET=US Growth
if "%CHOICE%"=="8" goto :list_presets

if "%CHOICE%"=="7" (
    echo.
    set /p SYMBOLS="Enter US symbols (comma-separated, e.g., AAPL,MSFT,GOOGL): "
    echo.
    set /p CAPITAL="Enter initial capital in USD (default: 100000): "
    if "!CAPITAL!"=="" set CAPITAL=100000
    
    echo.
    echo Starting US Pipeline with custom symbols...
    echo Symbols: !SYMBOLS!
    echo Capital: $!CAPITAL! USD
    echo.
    python run_us_pipeline.py --symbols "!SYMBOLS!" --capital !CAPITAL!
    goto :end
)

if not defined PRESET (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
set /p CAPITAL="Enter initial capital in USD (default: 100000): "
if "%CAPITAL%"=="" set CAPITAL=100000

echo.
set /p IGNORE_HOURS="Ignore market hours? (y/N): "

echo.
echo Starting US Pipeline...
echo Preset: %PRESET%
echo Capital: $%CAPITAL% USD
echo.

if /i "%IGNORE_HOURS%"=="y" (
    python run_us_pipeline.py --preset "%PRESET%" --capital %CAPITAL% --ignore-market-hours
) else (
    python run_us_pipeline.py --preset "%PRESET%" --capital %CAPITAL%
)
goto :end

:list_presets
python run_us_pipeline.py --list-presets
pause
exit /b 0

:end
pause

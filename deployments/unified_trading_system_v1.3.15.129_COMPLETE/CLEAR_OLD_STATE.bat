@echo off
REM Clear Old Trading State - Fix for Auto-Appearing Positions
REM ============================================================

echo.
echo ============================================================
echo CLEAR OLD TRADING STATE
echo ============================================================
echo.
echo This script will clear old positions from previous sessions
echo so the dashboard starts fresh with no automatic positions.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Change to script directory
cd /d "%~dp0"

echo.
echo [1] Checking for state file...
if exist "state\paper_trading_state.json" (
    echo     Found: state\paper_trading_state.json
    echo.
    echo [2] Backing up current state...
    copy "state\paper_trading_state.json" "state\paper_trading_state_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.json" >nul 2>&1
    echo     Backup created: paper_trading_state_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.json
    echo.
    echo [3] Deleting old state...
    del "state\paper_trading_state.json"
    echo     Deleted successfully
    echo.
    echo [OK] Old positions cleared!
    echo.
    echo Next time you start the dashboard, it will be completely clean.
    echo No automatic positions will appear.
    echo.
) else (
    echo     No state file found - already clean!
    echo.
)

echo.
echo ============================================================
echo DONE
echo ============================================================
echo.
echo Next Steps:
echo 1. Start the dashboard with START.bat
echo 2. Select your symbols (or choose a preset)
echo 3. Click "Start Trading" to begin
echo.
echo Note: A backup of your old state was saved to:
echo       state\paper_trading_state_backup_*.json
echo.
pause

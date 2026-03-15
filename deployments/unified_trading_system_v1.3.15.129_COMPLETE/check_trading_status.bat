@echo off
echo ============================================================
echo UK TRADING STATUS CHECK
echo ============================================================
echo Time: %date% %time%
echo.

echo Checking trading state...
if exist state\paper_trading_state.json (
    echo [OK] Trading state file exists
    type state\paper_trading_state.json
) else (
    echo [X] Trading state NOT found - System not started!
)
echo.

echo Checking recent logs...
if exist logs\paper_trading.log (
    echo [OK] Trading log exists
    echo Last 20 lines:
    powershell -Command "Get-Content logs\paper_trading.log -Tail 20"
) else (
    echo [X] Trading log NOT found
)
echo.

echo Checking dashboard log...
if exist logs\unified_trading.log (
    echo [OK] Dashboard log exists
    echo Last 20 lines:
    powershell -Command "Get-Content logs\unified_trading.log -Tail 20"
) else (
    echo [X] Dashboard log NOT found
)

echo.
echo ============================================================
pause

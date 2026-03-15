@echo off
setlocal enabledelayedexpansion

echo ========================================
echo UNIFIED TRADING DIAGNOSTIC TOOL
echo ========================================
echo System: v1.3.15.45 FINAL
echo Time: %date% %time%
echo ========================================
echo.

REM Check 1: Log Files
echo [1] CHECKING LOG FILES...
echo.
if exist logs\unified_trading.log (
    echo [OK] unified_trading.log exists
    for /f %%a in ('powershell "(Get-Item logs\unified_trading.log).length / 1KB"') do set size=%%a
    echo     Size: !size! KB
    echo.
    echo     Last 10 lines:
    echo     ----------------------------------------
    powershell "Get-Content logs\unified_trading.log -Tail 10 -ErrorAction SilentlyContinue"
    echo     ----------------------------------------
) else (
    echo [ERROR] unified_trading.log NOT FOUND
    echo         Trading system may not have started!
)
echo.

REM Check 2: Paper Trading Log
echo [2] CHECKING PAPER TRADING LOG...
echo.
if exist logs\paper_trading.log (
    echo [OK] paper_trading.log exists
    for /f %%a in ('powershell "(Get-Item logs\paper_trading.log).length / 1KB"') do set size=%%a
    echo     Size: !size! KB
    echo.
    echo     Last 5 lines:
    echo     ----------------------------------------
    powershell "Get-Content logs\paper_trading.log -Tail 5 -ErrorAction SilentlyContinue"
    echo     ----------------------------------------
) else (
    echo [INFO] paper_trading.log not found (may not have started yet)
)
echo.

REM Check 3: State File
echo [3] CHECKING STATE FILE...
echo.
if exist state\paper_trading_state.json (
    echo [OK] paper_trading_state.json exists
    for /f %%a in ('powershell "(Get-Item state\paper_trading_state.json).length / 1KB"') do set size=%%a
    echo     Size: !size! KB
    echo.
    echo     Contents:
    echo     ----------------------------------------
    type state\paper_trading_state.json
    echo     ----------------------------------------
) else (
    echo [ERROR] paper_trading_state.json NOT FOUND
    echo         Trading system has not saved state yet!
    echo         This means trading thread may not be running.
)
echo.

REM Check 4: Market Hours
echo [4] CHECKING MARKET HOURS...
echo.
echo Current Time (Local): %date% %time%
echo.
echo Market Status at 18:00-19:00 GMT:
echo   US Markets (NYSE/NASDAQ):
echo     - AAPL, MSFT
echo     - Hours: 14:30-21:00 GMT (9:30 AM - 4:00 PM EST)
echo     - Status: LIKELY OPEN
echo.
echo   AU Market (ASX):
echo     - CBA.AX, BHP.AX
echo     - Hours: 23:00-06:00 GMT (next day)
echo     - Status: CLOSED (opens 23:00 GMT)
echo.
echo   UK Market (LSE):
echo     - HSBA.L, STAN.L, NWG.L, BHP.L, RIO.L
echo     - Hours: 08:00-16:30 GMT
echo     - Status: CLOSED (closed at 16:30 GMT)
echo.
echo RESULT: Only 2/9 stocks tradeable now (AAPL, MSFT)
echo.

REM Check 5: Config File
echo [5] CHECKING CONFIGURATION...
echo.
if exist config\screening_config.json (
    echo [OK] screening_config.json exists
    echo.
    echo Confidence Threshold:
    findstr /C:"confidence_threshold" config\screening_config.json
    echo.
    echo Risk Management:
    findstr /C:"max_position_size_pct\|max_total_positions" config\screening_config.json
) else (
    echo [WARN] screening_config.json not found
    echo        Using default settings
)
echo.

REM Check 6: Trading Cycle Detection
echo [6] DETECTING TRADING ACTIVITY...
echo.
if exist logs\unified_trading.log (
    set found_cycle=0
    findstr /C:"[CYCLE]" logs\unified_trading.log >nul 2>&1
    if !errorlevel! equ 0 (
        set found_cycle=1
        echo [OK] Trading cycles detected in logs!
        echo.
        echo Recent cycles:
        findstr /C:"[CYCLE]" logs\unified_trading.log | powershell "Select-Object -Last 5"
    ) else (
        echo [ERROR] NO TRADING CYCLES DETECTED!
        echo         Trading loop may not be running.
    )
    
    if !found_cycle! equ 1 (
        echo.
        echo Recent signals:
        findstr /C:"Signal\|HOLD\|BUY\|SELL" logs\unified_trading.log | powershell "Select-Object -Last 5"
    )
) else (
    echo [ERROR] Cannot check - log file not found
)
echo.

REM Diagnosis Summary
echo ========================================
echo DIAGNOSIS SUMMARY
echo ========================================
echo.

if not exist logs\unified_trading.log (
    echo [CRITICAL] Trading system NOT running
    echo            No log file found
    echo.
    echo ACTION: Restart the unified trading dashboard
    goto :end
)

if not exist state\paper_trading_state.json (
    echo [CRITICAL] Trading thread NOT active
    echo            No state file created
    echo.
    echo ACTION: Click "Start Trading" button in dashboard
    goto :end
)

findstr /C:"[CYCLE]" logs\unified_trading.log >nul 2>&1
if !errorlevel! neq 0 (
    echo [CRITICAL] Trading loop NOT running
    echo            No cycles detected in logs
    echo.
    echo ACTION: Stop and restart trading in dashboard
    goto :end
)

REM If we got here, system is running
echo [OK] Trading system is RUNNING
echo.
findstr /C:"BUY\|SELL" logs\unified_trading.log >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Trades have been executed
    echo.
    echo Recent trades:
    findstr /C:"BUY\|SELL" logs\unified_trading.log | powershell "Select-Object -Last 3"
) else (
    echo [INFO] NO TRADES YET
    echo.
    echo Possible reasons:
    echo   1. Market conditions neutral (confidence below threshold)
    echo   2. Most stocks in closed markets (7/9 closed at 18:00 GMT)
    echo   3. System being selective (waiting for better signals)
    echo.
    echo This is NORMAL if:
    echo   - Running for less than 1 hour
    echo   - Confidence threshold is high (60-70+)
    echo   - Market conditions are neutral
    echo.
    echo ACTION: Be patient OR restart with only US stocks (AAPL,MSFT)
)

:end
echo.
echo ========================================
echo DIAGNOSTIC COMPLETE
echo ========================================
echo.
pause

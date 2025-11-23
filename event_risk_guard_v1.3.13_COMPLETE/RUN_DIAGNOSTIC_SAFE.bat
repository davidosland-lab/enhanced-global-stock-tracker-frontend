@echo off
REM ============================================================================
REM SAFE Diagnostic Wrapper - GUARANTEES window stays open
REM ============================================================================
REM This wrapper ensures the diagnostic window NEVER closes without user input
REM Even if the diagnostic script crashes, this wrapper will catch it
REM ============================================================================

echo.
echo ================================================================================
echo SAFE DIAGNOSTIC WRAPPER
echo ================================================================================
echo.
echo This wrapper will run the diagnostic and GUARANTEE the window stays open.
echo.
echo Starting diagnostic in 2 seconds...
timeout /t 2 >nul
echo.

REM Run the diagnostic in a way that captures all output
call DIAGNOSE_REGIME_ENGINE.bat

REM This line ALWAYS executes, even if above script fails
echo.
echo.
echo ================================================================================
echo DIAGNOSTIC COMPLETED (or failed)
echo ================================================================================
echo.
echo The diagnostic has finished running.
echo Please scroll up to see all the output above.
echo.
echo.
echo *** WINDOW WILL NOT CLOSE UNTIL YOU PRESS A KEY ***
echo.
pause
echo.
echo Closing window...
timeout /t 2 >nul
exit /b 0

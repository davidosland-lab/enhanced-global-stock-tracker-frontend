@echo off
REM ============================================================================
REM Diagnostic with Log File - Output saved to file
REM ============================================================================
REM This version saves ALL output to a text file AND keeps window open
REM ============================================================================

echo.
echo ================================================================================
echo DIAGNOSTIC WITH LOG FILE
echo ================================================================================
echo.
echo This will run the diagnostic and save output to: diagnostic_output.txt
echo.
echo Starting in 2 seconds...
timeout /t 2 >nul
echo.

REM Run Python diagnostic and save to file
echo Running diagnostic...
python diagnose_regime.py > diagnostic_output.txt 2>&1

REM Check if it succeeded
if exist diagnostic_output.txt (
    echo.
    echo ================================================================================
    echo DIAGNOSTIC COMPLETE!
    echo ================================================================================
    echo.
    echo Output has been saved to: diagnostic_output.txt
    echo.
    echo Opening the log file now...
    echo.
    timeout /t 2 >nul
    
    REM Open the file in notepad
    start notepad diagnostic_output.txt
    
    echo.
    echo The diagnostic output is now open in Notepad.
    echo You can read it, save it, or copy it from there.
    echo.
    echo *** THIS WINDOW WILL NOT CLOSE UNTIL YOU PRESS A KEY ***
    echo.
    pause
) else (
    echo.
    echo ERROR: Diagnostic failed to create output file.
    echo.
    pause
)

exit /b 0

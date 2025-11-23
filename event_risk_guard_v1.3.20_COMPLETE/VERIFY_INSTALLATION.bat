@echo off
REM ============================================================================
REM VERIFY_INSTALLATION.bat - Installation Verification Wrapper
REM ============================================================================
REM
REM This script runs the Python verification script and ensures the window
REM stays open so you can read the results.
REM
REM Usage: Just double-click VERIFY_INSTALLATION.bat
REM ============================================================================

echo.
echo ================================================================================
echo OVERNIGHT SCREENER v1.3.14 - INSTALLATION VERIFICATION
echo ================================================================================
echo.
echo Running comprehensive installation checks...
echo This will verify:
echo   1. File structure (all critical files present)
echo   2. Python packages (torch, transformers, tensorflow, etc.)
echo   3. FinBERT Bridge functional
echo   4. Configuration correct
echo   5. PHASE 4.5 code exists
echo   6. Regime Engine integration exists
echo.
echo ================================================================================
echo.

REM Run the Python verification script
python VERIFY_INSTALLATION.py

REM Store exit code
set EXIT_CODE=%ERRORLEVEL%

echo.
echo ================================================================================
echo.

if %EXIT_CODE% EQU 0 (
    echo [SUCCESS] All verification checks passed!
    echo.
    echo Next Steps:
    echo   1. Run the pipeline: RUN_PIPELINE.bat --test  (quick verification^)
    echo   2. Or run full pipeline: RUN_PIPELINE.bat     (complete analysis^)
) else (
    echo [WARNING] Some verification checks failed.
    echo.
    echo Troubleshooting:
    echo   1. Check if all files were extracted from ZIP
    echo   2. Run INSTALL.bat to install missing packages
    echo   3. Review error messages above
    echo   4. See INSTALLATION_ISSUES_EXPLAINED.md for help
)

echo.
echo ================================================================================
echo.

REM Pause so user can read results
pause

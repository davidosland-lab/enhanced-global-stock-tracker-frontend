@echo off
REM ==============================================================================
REM RUN TESTS - Event Risk Guard v1.1
REM ==============================================================================
REM
REM Runs unit tests for Factor View and Macro Beta modules
REM
REM Usage: Double-click this file or run from command line
REM ==============================================================================

echo.
echo ================================================================================
echo EVENT RISK GUARD v1.1 - TEST RUNNER
echo ================================================================================
echo.

REM Run all tests
echo Running unit tests...
echo.

python -m unittest discover -s tests -p "test_*.py" -v

echo.
echo ================================================================================
echo Test run complete!
echo ================================================================================
echo.

pause

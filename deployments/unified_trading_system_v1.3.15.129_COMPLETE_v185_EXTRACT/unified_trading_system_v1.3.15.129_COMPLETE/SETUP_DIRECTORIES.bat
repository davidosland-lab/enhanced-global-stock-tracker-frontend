@echo off
REM Setup Required Directories for Overnight Pipelines
REM Creates all necessary log and report directories

chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ================================================================================
echo DIRECTORY SETUP - Overnight Pipelines v1.3.15.87
echo ================================================================================
echo.
echo Creating required directories...
echo.

REM Create logs directories
mkdir "%~dp0logs" 2>nul
mkdir "%~dp0logs\screening" 2>nul
mkdir "%~dp0logs\screening\au" 2>nul
mkdir "%~dp0logs\screening\us" 2>nul
mkdir "%~dp0logs\screening\uk" 2>nul
mkdir "%~dp0logs\screening\errors" 2>nul
mkdir "%~dp0logs\screening\au\errors" 2>nul
mkdir "%~dp0logs\screening\us\errors" 2>nul
mkdir "%~dp0logs\screening\uk\errors" 2>nul

REM Create reports directories
mkdir "%~dp0reports" 2>nul
mkdir "%~dp0reports\screening" 2>nul
mkdir "%~dp0reports\csv_exports" 2>nul
mkdir "%~dp0reports\pipeline_state" 2>nul

REM Create data directories
mkdir "%~dp0data" 2>nul
mkdir "%~dp0data\au" 2>nul
mkdir "%~dp0data\us" 2>nul
mkdir "%~dp0data\uk" 2>nul

REM Create config directory
mkdir "%~dp0config" 2>nul

REM Create state directory
mkdir "%~dp0state" 2>nul

echo [OK] Directory structure created:
echo.
echo logs/
echo   screening/
echo     au/
echo       errors/
echo     us/
echo       errors/
echo     uk/
echo       errors/
echo.
echo reports/
echo   screening/
echo   csv_exports/
echo   pipeline_state/
echo.
echo data/
echo   au/
echo   us/
echo   uk/
echo.
echo config/
echo state/
echo.
echo ================================================================================
echo SETUP COMPLETE
echo ================================================================================
echo.
echo You can now run the overnight pipelines:
echo   cd pipelines
echo   RUN_AU_PIPELINE.bat
echo   RUN_US_PIPELINE.bat
echo   RUN_UK_PIPELINE.bat
echo.
echo ================================================================================
echo.

exit /b 0

@echo off
REM Quick Update Script for v1.3.20 Patch
REM This script applies the bug fix updates to your existing installation

echo ========================================
echo Dual Market Stock Screener - Update v1.3.20 Patch
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "models\screening" (
    echo ERROR: This script must be run from the deployment_dual_market_v1.3.20_CLEAN directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Step 1: Backing up files...
echo.

REM Create backup directory
if not exist "backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%" (
    mkdir "backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%"
)

REM Backup critical files
if exist "models\screening\chatgpt_research.py" (
    copy "models\screening\chatgpt_research.py" "backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%\chatgpt_research.py.backup"
    echo   - Backed up chatgpt_research.py
)

if exist "models\screening\us_overnight_pipeline.py" (
    copy "models\screening\us_overnight_pipeline.py" "backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%\us_overnight_pipeline.py.backup"
    echo   - Backed up us_overnight_pipeline.py
)

echo.
echo Step 2: Clearing Python cache...
echo.

REM Clear Python cache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo   - Python cache cleared
echo.
echo Step 3: Update applied successfully!
echo.

REM Check if the files exist (they should if this script is in the extracted update)
if exist "models\screening\chatgpt_research.py" (
    echo   - chatgpt_research.py updated
) else (
    echo   WARNING: chatgpt_research.py not found
)

if exist "models\screening\us_overnight_pipeline.py" (
    echo   - us_overnight_pipeline.py updated
) else (
    echo   WARNING: us_overnight_pipeline.py not found
)

if exist "DIAGNOSE_PIPELINE.py" (
    echo   - DIAGNOSE_PIPELINE.py added
)

if exist "TEST_REPORT_GENERATION.py" (
    echo   - TEST_REPORT_GENERATION.py added
)

echo.
echo ========================================
echo Update Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run diagnostics: python DIAGNOSE_PIPELINE.py
echo   2. Test reports:    python TEST_REPORT_GENERATION.py
echo   3. Next pipeline run will use the fixed code
echo.
echo Your trained models are safe in: finbert_v4.4.4\models\trained\
echo Backups saved to: backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%\
echo.
pause

@echo off
echo ================================================================================
echo MANUAL START - MINIMAL REQUIREMENTS
echo ================================================================================
echo.

REM Clear any problematic environment
if exist ".env" del /f /q ".env"
SET FLASK_SKIP_DOTENV=1
SET PYTHONIOENCODING=utf-8

echo Try starting with Python directly...
echo.
echo If this fails, note the EXACT error message
echo ================================================================================
echo.

python app_finbert_ultimate_av.py

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo Server failed to start. Trying alternative method...
    echo ================================================================================
    echo.
    
    REM Try with explicit Python path if available
    if exist "C:\Python312\python.exe" (
        "C:\Python312\python.exe" app_finbert_ultimate_av.py
    ) else if exist "C:\Python311\python.exe" (
        "C:\Python311\python.exe" app_finbert_ultimate_av.py
    ) else if exist "C:\Python310\python.exe" (
        "C:\Python310\python.exe" app_finbert_ultimate_av.py
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" app_finbert_ultimate_av.py
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" app_finbert_ultimate_av.py
    ) else (
        echo Could not find Python installation
    )
)

pause
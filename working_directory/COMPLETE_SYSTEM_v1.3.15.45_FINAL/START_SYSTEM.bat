@echo off
REM Simple wrapper to launch Python-based installer
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe launcher.py
) else (
    python launcher.py
)

pause

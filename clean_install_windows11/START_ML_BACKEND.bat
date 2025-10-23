@echo off
echo Starting ML Backend on port 8003...
if exist backend_ml_enhanced.py (
    python backend_ml_enhanced.py
) else (
    echo ERROR: backend_ml_enhanced.py not found!
    echo Please ensure all files are extracted from the zip.
    pause
)

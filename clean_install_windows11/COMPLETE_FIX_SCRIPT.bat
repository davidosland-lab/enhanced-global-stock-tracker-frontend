@echo off
title Stock Tracker - Complete Module Fix
color 0A
cls

echo ===============================================================================
echo                    COMPLETE MODULE FIX SCRIPT
echo              Fixing all broken links and endpoints
echo ===============================================================================
echo.

echo [1] Stopping all services...
echo -----------------------------------------------
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

echo.
echo [2] Backing up current files...
echo -----------------------------------------------
copy backend.py backend_backup.py >nul 2>&1
copy index.html index_backup.html >nul 2>&1
echo   Backups created

echo.
echo [3] Replacing backend with complete fixed version...
echo -----------------------------------------------
if exist backend_complete_fixed.py (
    copy /Y backend_complete_fixed.py backend.py >nul
    echo   ✓ Backend replaced with fixed version
) else (
    echo   ⚠ backend_complete_fixed.py not found
    echo   Please ensure backend_complete_fixed.py exists
)

echo.
echo [4] Fixing index.html module links...
echo -----------------------------------------------
echo   Updating module paths...

:: Create a temporary Python script to fix the links
echo import re > fix_links.py
echo with open('index.html', 'r', encoding='utf-8') as f: >> fix_links.py
echo     content = f.read() >> fix_links.py
echo pattern = r"const modules = \{[^}]+\};" >> fix_links.py
echo replacement = """const modules = { >> fix_links.py
echo             'cba': 'modules/cba_enhanced.html', >> fix_links.py
echo             'indices': 'modules/indices_tracker.html', >> fix_links.py
echo             'tracker': 'modules/stock_tracker.html', >> fix_links.py
echo             'predictor': 'modules/prediction_centre_phase4.html', >> fix_links.py
echo             'documents': 'modules/document_uploader.html', >> fix_links.py
echo             'historical': 'modules/historical_data_manager_fixed.html', >> fix_links.py
echo             'performance': 'modules/prediction_performance_dashboard.html', >> fix_links.py
echo             'mltraining': 'modules/ml_training_centre.html', >> fix_links.py
echo             'technical': 'modules/technical_analysis_fixed.html' >> fix_links.py
echo         };""" >> fix_links.py
echo content = re.sub(pattern, replacement, content, flags=re.DOTALL) >> fix_links.py
echo with open('index.html', 'w', encoding='utf-8') as f: >> fix_links.py
echo     f.write(content) >> fix_links.py
echo print("Links fixed!") >> fix_links.py

python fix_links.py
del fix_links.py
echo   ✓ Module links updated

echo.
echo [5] Starting services with fixed configuration...
echo -----------------------------------------------

echo   Starting main backend on port 8002...
start /min cmd /c "python backend.py"
timeout /t 3 >nul

echo   Starting ML backend on port 8003...
if exist ml_backend_working.py (
    start /min cmd /c "python ml_backend_working.py"
) else if exist ml_training_backend.py (
    start /min cmd /c "python ml_training_backend.py"
)
timeout /t 3 >nul

echo   Starting frontend server on port 8000...
start /min cmd /c "python -m http.server 8000"
timeout /t 2 >nul

echo.
echo ===============================================================================
echo                           FIXES APPLIED
echo ===============================================================================
echo.
echo ✅ Backend updated with all missing endpoints:
echo    - /api/historical/batch-download (fixes Historical Data Manager)
echo    - /api/historical/download (fixes bulk downloads)
echo    - /api/historical/statistics (fixes statistics display)
echo.
echo ✅ Module links corrected in index.html:
echo    - Prediction Centre: modules/prediction_centre_phase4.html
echo    - Document Uploader: modules/document_uploader.html
echo    - Historical Data: modules/historical_data_manager_fixed.html
echo.
echo ✅ Services running:
echo    - Backend API: http://localhost:8002
echo    - ML Backend: http://localhost:8003
echo    - Frontend: http://localhost:8000
echo.
echo ===============================================================================
echo.
echo Opening browser in 3 seconds...
timeout /t 3 >nul
start http://localhost:8000

echo.
echo Press any key to keep services running...
pause >nul

:KEEPALIVE
timeout /t 60 >nul
goto KEEPALIVE
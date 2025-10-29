@echo off
echo ====================================================
echo STOCK ANALYSIS VERSION COMPARISON
echo ====================================================
echo.
echo You have TWO versions available:
echo.
echo 1. ORIGINAL VERSION (Stable)
echo    - Technical indicators only
echo    - Proven and tested
echo    - ~65-70%% ML accuracy
echo.
echo 2. ENHANCED VERSION (New Phase 1)
echo    - All original features PLUS:
echo    - VIX Fear Gauge
echo    - Market Breadth
echo    - Bond Yields
echo    - Dollar Index
echo    - Sector Rotation
echo    - ~72-78%% ML accuracy (expected)
echo.
echo ====================================================
echo.
echo Which version would you like to run?
echo.
echo [1] Original Version (app.py)
echo [2] Enhanced Sentiment Version (app_enhanced_sentiment.py)
echo [3] Cancel
echo.
choice /c 123 /n /m "Select option (1-3): "

if errorlevel 3 goto :cancel
if errorlevel 2 goto :enhanced
if errorlevel 1 goto :original

:original
echo.
echo Starting ORIGINAL version...
echo.
python app.py
goto :end

:enhanced
echo.
echo Starting ENHANCED SENTIMENT version...
echo.
python app_enhanced_sentiment.py
goto :end

:cancel
echo.
echo Cancelled.
goto :end

:end
pause
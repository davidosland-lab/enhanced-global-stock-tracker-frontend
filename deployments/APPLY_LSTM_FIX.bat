@echo off
REM ============================================
REM LSTM Mock Sentiment Fix Installer
REM Version: v1.3.15.152+
REM Date: 2026-02-17
REM ============================================

echo.
echo ============================================
echo LSTM MOCK SENTIMENT FIX INSTALLER
echo ============================================
echo.
echo This script will fix the error:
echo 'FinBERTSentimentAnalyzer' object has no attribute 'get_mock_sentiment'
echo.

REM Check if running in correct directory
if not exist "finbert_v4.4.4\models\lstm_predictor.py" (
    echo ERROR: This script must be run from the root of unified_trading_system_v1.3.15.129_COMPLETE
    echo.
    echo Current directory: %CD%
    echo Expected directory: C:\Users\david\REgime trading V4 restored\unified_trading_system_v1.3.15.129_COMPLETE
    echo.
    pause
    exit /b 1
)

echo [1/5] Creating backup directory...
if not exist "backup_20260217" mkdir backup_20260217

echo [2/5] Backing up current files...
copy finbert_v4.4.4\models\lstm_predictor.py backup_20260217\ > nul
copy finbert_v4.4.4\models\finbert_sentiment.py backup_20260217\ > nul
echo     ✓ Backed up to backup_20260217\

echo [3/5] Clearing Python cache...
if exist "finbert_v4.4.4\models\__pycache__" rd /s /q finbert_v4.4.4\models\__pycache__
echo     ✓ Cache cleared

echo [4/5] Applying fixes...
echo.
echo     Please manually replace these two files:
echo.
echo     1. finbert_v4.4.4\models\lstm_predictor.py
echo     2. finbert_v4.4.4\models\finbert_sentiment.py
echo.
echo     Download fixed files from sandbox:
echo     /home/user/webapp/deployments/unified_trading_system_v1.3.15.129_COMPLETE/finbert_v4.4.4/models/
echo.

pause

echo [5/5] Testing fix...
echo.
echo Running test with WOW.AX...
echo.

python scripts\run_uk_full_pipeline.py --symbols WOW.AX

echo.
echo ============================================
echo FIX INSTALLATION COMPLETE
echo ============================================
echo.
echo Next steps:
echo 1. Check the output above for "LSTM prediction for WOW.AX: BUY"
echo 2. If successful, run full pipeline: python scripts\run_uk_full_pipeline.py
echo 3. Verify LSTM success rate ^>90%%
echo.
pause

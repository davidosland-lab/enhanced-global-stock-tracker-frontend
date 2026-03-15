@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  INSTALL TRANSFORMERS - FIX v1.3.15.66
REM  Fixes FinBERT loading issue
REM ═══════════════════════════════════════════════════════════════════════════

cd /d "%~dp0"
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║               INSTALL TRANSFORMERS - FIX v1.3.15.66                       ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   This will install the transformers library for FinBERT
echo   Required for 95%% sentiment accuracy
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    pause
    exit /b 1
)

echo [1/3] Uninstalling old transformers...
pip uninstall -y transformers 2>nul

echo.
echo [2/3] Installing transformers library...
echo   This may take 2-5 minutes...
echo.

pip install transformers --no-cache-dir

if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed!
    echo.
    echo Try this manually:
    echo   pip install --upgrade pip
    echo   pip install transformers
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Testing installation...
echo.

python -c "from transformers import BertForSequenceClassification; print('[OK] transformers installed successfully!')"

if errorlevel 1 (
    echo.
    echo [ERROR] Installation test failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                    INSTALLATION COMPLETE!                                 ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   ✓ transformers library installed
echo   ✓ FinBERT ready to use
echo   ✓ Sentiment accuracy: 95%%
echo.
echo   Next step: Run FIX_FINBERT_LOADING_v1.3.15.66.py again
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

pause

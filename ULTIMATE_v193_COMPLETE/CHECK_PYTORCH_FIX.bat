@echo off
REM Quick check if PyTorch fix is applied

echo Checking if PyTorch fix is applied...
echo.

cd /d "%~dp0"

python -c "import sys; sys.path.insert(0, 'finbert_v4.4.4/models'); f = open('finbert_v4.4.4/models/finbert_sentiment.py', 'r', encoding='utf-8'); content = f.read(); f.close(); has_detach = '.detach().cpu().numpy()' in content; print('✓ Fix IS applied - .detach() found' if has_detach else '✗ Fix NOT applied - .detach() missing'); sys.exit(0 if has_detach else 1)"

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo   FIX NOT APPLIED - ACTION REQUIRED
    echo ===============================================================================
    echo.
    echo You need to edit this file:
    echo   finbert_v4.4.4\models\finbert_sentiment.py
    echo.
    echo Find line 177 with:
    echo   probs = predictions[0].cpu^(^).numpy^(^)
    echo.
    echo Change to:
    echo   probs = predictions[0].detach^(^).cpu^(^).numpy^(^)
    echo.
    echo Just add .detach^(^) before .cpu^(^)
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   FIX IS APPLIED
echo ================================================================================
echo.
echo The PyTorch fix is already applied in your system.
echo If you're still getting the error, it might be a different issue.
echo.
pause

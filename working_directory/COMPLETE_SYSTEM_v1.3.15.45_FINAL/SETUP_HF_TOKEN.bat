@echo off
SETLOCAL
COLOR 0B
CLS

echo ================================================================================
echo   HUGGING FACE TOKEN SETUP
echo   Optional: Faster downloads and higher rate limits
echo ================================================================================
echo.
echo This script helps you set up a Hugging Face token (optional).
echo.
echo Benefits of setting a token:
echo   - Faster model downloads
echo   - Higher rate limits (1000 vs 20 requests/hour)
echo   - Access to private models (if you have any)
echo.
echo Without a token:
echo   - Models still download (just slower)
echo   - Fine for normal daily use
echo   - May hit rate limits with heavy use
echo.
echo ================================================================================
echo.

:MENU
echo Choose an option:
echo   [1] I have a token - Set it now
echo   [2] I need to get a token - Show me how
echo   [3] Skip this - I'll set it up later
echo   [0] Exit
echo.
set /p choice="Enter choice (0-3): "

if "%choice%"=="1" goto SET_TOKEN
if "%choice%"=="2" goto GET_TOKEN
if "%choice%"=="3" goto SKIP
if "%choice%"=="0" goto END
goto MENU

:GET_TOKEN
cls
echo ================================================================================
echo   HOW TO GET A HUGGING FACE TOKEN (FREE)
echo ================================================================================
echo.
echo Step 1: Create Account (if you don't have one)
echo   1. Go to: https://huggingface.co/
echo   2. Click "Sign Up" (top right)
echo   3. Use email or Google/GitHub account
echo   4. Verify your email
echo.
echo Step 2: Create Token
echo   1. Go to: https://huggingface.co/settings/tokens
echo   2. Click "New token"
echo   3. Name: "finbert_token" (or any name)
echo   4. Type: "Read" (default - safe)
echo   5. Click "Generate"
echo   6. COPY the token (starts with hf_...)
echo.
echo Step 3: Come back here and choose option [1]
echo.
echo ================================================================================
echo.
pause
goto MENU

:SET_TOKEN
cls
echo ================================================================================
echo   SET HUGGING FACE TOKEN
echo ================================================================================
echo.
echo Paste your token below (starts with hf_...)
echo.
echo Your token will be saved to:
echo   - Environment variable: HF_TOKEN
echo   - Stored permanently (survives reboots)
echo.
set /p token="Enter token: "

if "%token%"=="" (
    echo [ERROR] No token entered!
    echo.
    pause
    goto MENU
)

REM Validate token format
echo %token% | findstr /B "hf_" >nul
if errorlevel 1 (
    echo [WARN] Token doesn't start with hf_ - are you sure it's correct?
    echo.
    set /p confirm="Continue anyway? (Y/N): "
    if /i not "%confirm%"=="Y" goto MENU
)

REM Set token permanently
setx HF_TOKEN "%token%" >nul 2>&1

if errorlevel 1 (
    echo [ERROR] Failed to set token!
    echo [*] Try running as Administrator
    echo.
    pause
    goto MENU
)

REM Set for current session
set HF_TOKEN=%token%

echo.
echo [OK] Token set successfully!
echo.
echo What was done:
echo   - HF_TOKEN environment variable created
echo   - Token stored permanently
echo   - Available to all programs
echo.
echo ================================================================================
echo   VERIFICATION
echo ================================================================================
echo.
echo Testing token...

REM Test token with Python (if available)
where python >nul 2>&1
if not errorlevel 1 (
    echo.
    python -c "from huggingface_hub import whoami; print('[OK] Token valid:', whoami())" 2>nul
    if errorlevel 1 (
        echo [WARN] Could not verify token (Python/huggingface_hub not available)
        echo [*] Token is set, but validation failed
        echo [*] Try running your pipeline to verify
    )
) else (
    echo [*] Python not in PATH - token is set but not verified
    echo [*] Run your pipeline to verify token works
)

echo.
echo ================================================================================
echo   NEXT STEPS
echo ================================================================================
echo.
echo 1. RESTART your Command Prompt / Terminal
echo    (Required for token to be available to new processes)
echo.
echo 2. Run your pipeline:
echo    LAUNCH_COMPLETE_SYSTEM.bat
echo.
echo 3. You should see:
echo    - Faster downloads
echo    - No more "unauthenticated requests" warning
echo.
echo ================================================================================
echo.
pause
goto END

:SKIP
cls
echo ================================================================================
echo   SKIPPED TOKEN SETUP
echo ================================================================================
echo.
echo No problem! Your system works fine without a token.
echo.
echo You can set it up later by:
echo   1. Running this script again
echo   2. Manually: setx HF_TOKEN "hf_your_token_here"
echo   3. Adding to venv\Scripts\activate.bat
echo.
echo When to add a token:
echo   - If you see rate limit errors
echo   - If downloads are very slow
echo   - If you run pipelines very frequently
echo.
pause
goto END

:END
echo.
echo Exiting...
ENDLOCAL

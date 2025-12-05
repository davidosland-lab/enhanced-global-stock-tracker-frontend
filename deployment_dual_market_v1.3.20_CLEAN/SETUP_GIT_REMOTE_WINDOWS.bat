@echo off
REM ============================================================================
REM Setup Git Remote for AATelS Directory (Windows)
REM ============================================================================
REM This script configures the git remote for the local AATelS repository
REM and pulls the latest code from GitHub.
REM
REM Created: 2025-12-05
REM Repository: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
REM ============================================================================

echo.
echo ============================================================
echo Git Remote Setup for AATelS
echo ============================================================
echo.

REM Change to AATelS directory
cd /d C:\Users\david\AATelS
if errorlevel 1 (
    echo ERROR: Cannot access C:\Users\david\AATelS
    echo Please verify the directory exists.
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

REM Check if this is a git repository
if not exist ".git" (
    echo ERROR: This directory is not a git repository!
    echo.
    echo SOLUTION 1: Initialize as git repository and add remote
    echo ------------------------------------------------------------
    echo Run these commands:
    echo   git init
    echo   git remote add origin https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend.git
    echo   git fetch origin main
    echo   git reset --hard origin/main
    echo.
    echo SOLUTION 2: Clone fresh from GitHub
    echo ------------------------------------------------------------
    echo   cd C:\Users\david
    echo   rename AATelS AATelS_backup
    echo   git clone https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend.git AATelS
    echo.
    pause
    exit /b 1
)

echo Step 1: Checking current remote configuration...
echo ------------------------------------------------------------
git remote -v
echo.

echo Step 2: Removing any existing 'origin' remote...
echo ------------------------------------------------------------
git remote remove origin 2>nul
echo Origin remote cleared.
echo.

echo Step 3: Adding correct GitHub remote...
echo ------------------------------------------------------------
git remote add origin https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend.git
if errorlevel 1 (
    echo ERROR: Failed to add remote.
    pause
    exit /b 1
)
echo Remote added successfully!
echo.

echo Step 4: Verifying new remote configuration...
echo ------------------------------------------------------------
git remote -v
echo.

echo Step 5: Fetching latest code from GitHub...
echo ------------------------------------------------------------
git fetch origin main
if errorlevel 1 (
    echo ERROR: Failed to fetch from GitHub.
    echo Please check your internet connection and GitHub access.
    pause
    exit /b 1
)
echo Fetch successful!
echo.

echo Step 6: Checking current branch...
echo ------------------------------------------------------------
git branch
echo.

echo Step 7: Pulling latest changes...
echo ------------------------------------------------------------
git pull origin main
if errorlevel 1 (
    echo WARNING: Pull failed - you may have local changes.
    echo.
    echo To force update to latest GitHub version (WARNING: loses local changes):
    echo   git reset --hard origin/main
    echo.
) else (
    echo Pull successful!
)
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Your AATelS directory is now connected to:
echo https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
echo.
echo Next steps:
echo 1. Test the Intraday Monitor:
echo    python models/scheduling/intraday_scheduler.py
echo.
echo 2. Run Phase 1 ^& 2 Backtest Demo:
echo    python finbert_v4.4.4/models/backtesting/phase1_phase2_example.py
echo.
pause

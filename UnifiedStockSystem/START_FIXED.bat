@echo off
REM Simplified launcher that keeps window open using cmd /k
REM This ensures the window doesn't close immediately

echo Starting Unified Stock Analysis System...
echo.

REM Use cmd /k to keep the window open after execution
cmd /k python stock_analysis_unified_fixed.py
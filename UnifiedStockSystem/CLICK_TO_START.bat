@echo off
title Stock Analysis System
color 0A
cls

echo ========================================
echo     STOCK ANALYSIS SYSTEM
echo     Fixed Version - No Mock Data
echo ========================================
echo.

REM This keeps the window open no matter what happens
cmd /c python stock_analysis_unified_fixed.py & pause
@echo off
REM ================================================================================
REM LSTM TRAINING HOT-PATCH - v1.3.15.87
REM ================================================================================
REM
REM Quick patch to fix Flask routes for symbols with dots (BHP.AX, HSBA.L, etc.)
REM Can be applied while the dashboard is running.
REM
REM ================================================================================

python PATCH_LSTM_TRAINING.py

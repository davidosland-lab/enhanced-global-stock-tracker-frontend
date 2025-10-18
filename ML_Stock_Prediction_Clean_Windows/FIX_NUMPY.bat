@echo off
echo =====================================
echo FIXING NUMPY COMPATIBILITY ISSUE
echo =====================================
echo.
echo Problem: NumPy 2.x breaks scikit-learn
echo Solution: Downgrade to NumPy 1.26.4
echo.
echo This will fix the ML system...
echo.

python fix_numpy.py

echo.
pause
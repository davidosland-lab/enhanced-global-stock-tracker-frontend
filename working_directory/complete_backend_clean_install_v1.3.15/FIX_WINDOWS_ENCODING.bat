@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  Windows Encoding Fix - Removes Unicode emojis from Python files
REM  Version: 1.0
REM  Date: 2026-01-09
REM ═══════════════════════════════════════════════════════════════════════════

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   WINDOWS ENCODING FIX
echo   Replacing Unicode emojis with ASCII characters
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo [*] Setting UTF-8 encoding for Python files...

REM Fix all pipeline files
python -c "import sys, glob; [open(f, 'r+', encoding='utf-8').write(open(f, 'r', encoding='utf-8').read().replace('✓', '[OK]').replace('✗', '[X]').replace('⚠️', '[!]').replace('❌', '[X]').replace('🚀', '[=>]').replace('📊', '[#]').replace('💡', '[i]').replace('🎯', '[*]').replace('⭐', '[*]')) or print(f'Fixed: {f}') for f in glob.glob('*.py') + glob.glob('models/**/*.py', recursive=True)]"

echo.
echo [OK] Encoding fix complete!
echo.
echo All Unicode emojis replaced with ASCII equivalents:
echo   - Checkmark (✓) = [OK]
echo   - X mark (✗) = [X]
echo   - Warning (⚠️) = [!]
echo   - Red X (❌) = [X]
echo   - Rocket (🚀) = [=^>]
echo   - Chart (📊) = [#]
echo   - Bulb (💡) = [i]
echo   - Target (🎯) = [*]
echo   - Star (⭐) = [*]
echo.
pause

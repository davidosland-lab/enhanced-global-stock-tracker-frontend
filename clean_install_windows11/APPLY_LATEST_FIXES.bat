@echo off
echo ==========================================
echo Applying Latest Fixes (v17 patches)
echo ==========================================
echo.
echo This will update only the files that were fixed
echo without requiring a full redeployment.
echo.

:: Create a temporary Python script to apply the fixes
echo Creating fix script...
(
echo import os
echo import time
echo.
echo print("Applying ML Training Centre fixes..."^)
echo.
echo # Fix 1: Update ML Training Centre - fix endpoint URL
echo ml_training_file = "modules/ml_training_centre.html"
echo if os.path.exists(ml_training_file^):
echo     with open(ml_training_file, 'r', encoding='utf-8'^) as f:
echo         content = f.read(^)
echo     # Fix the training status endpoint URL
echo     content = content.replace('/api/ml/status/', '/api/ml/training/status/'^)
echo     with open(ml_training_file, 'w', encoding='utf-8'^) as f:
echo         f.write(content^)
echo     print("  ✓ Fixed ML training status endpoint URL"^)
echo.
echo print("Applying Backend fixes..."^)
echo.
echo # Fix 2: Check if historical/symbols endpoint exists in backend
echo backend_file = "backend.py"
echo if os.path.exists(backend_file^):
echo     with open(backend_file, 'r', encoding='utf-8'^) as f:
echo         content = f.read(^)
echo     # Check if the endpoint already exists
echo     if '/api/historical/symbols' not in content:
echo         print("  ! Historical symbols endpoint missing - please add manually"^)
echo         print("    or restart services with QUICK_RESTART.bat"^)
echo     else:
echo         print("  ✓ Historical symbols endpoint already present"^)
echo.
echo print("Applying Prediction Centre fixes..."^)
echo.
echo # Fix 3: Update Prediction Centre error handling
echo prediction_file = "modules/prediction_centre.html"
echo if os.path.exists(prediction_file^):
echo     with open(prediction_file, 'r', encoding='utf-8'^) as f:
echo         content = f.read(^)
echo     # Add error handling for historical endpoint
echo     if 'catch {' in content and 'console.log' not in content:
echo         content = content.replace('} catch {', '} catch (error^) {'
echo                                  'console.log("Historical endpoint check failed:", error.message^);'^)
echo         with open(prediction_file, 'w', encoding='utf-8'^) as f:
echo             f.write(content^)
echo         print("  ✓ Added error handling for historical endpoint"^)
echo     else:
echo         print("  ✓ Prediction Centre error handling already present"^)
echo.
echo print("\n✅ All fixes applied!"^)
echo print("Please use QUICK_RESTART.bat to restart services."^)
) > apply_fixes_temp.py

:: Run the Python script
python apply_fixes_temp.py

:: Clean up
del apply_fixes_temp.py

echo.
echo ==========================================
echo Fixes applied successfully!
echo ==========================================
echo.
echo Next steps:
echo 1. Run QUICK_RESTART.bat to restart services
echo 2. Refresh your browser (Ctrl+F5 for hard refresh)
echo.
pause
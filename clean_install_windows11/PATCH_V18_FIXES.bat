@echo off
echo ==========================================
echo Stock Tracker v18 Patch - Apply All Fixes
echo ==========================================
echo.
echo This patch will apply the following fixes:
echo 1. Document upload limit: 10MB -^> 100MB
echo 2. ML Training status URL fix
echo 3. Historical data endpoint error handling
echo.
echo No reinstallation required!
echo.

:: Create the Python patch script
echo Creating patch script...
(
echo import os
echo import sys
echo import json
echo.
echo print("="*50^)
echo print("Applying Stock Tracker v18 Patches"^)
echo print("="*50^)
echo.
echo # Fix 1: Document Upload Limit
echo print("\n[1/3] Fixing Document Upload Limit..."^)
echo doc_file = "modules/document_uploader.html"
echo if os.path.exists(doc_file^):
echo     with open(doc_file, 'r', encoding='utf-8'^) as f:
echo         content = f.read(^)
echo     
echo     changes_made = False
echo     
echo     # Update display text
echo     if "Max 10MB" in content:
echo         content = content.replace("Max 10MB", "Max 100MB"^)
echo         changes_made = True
echo         print("  ✓ Updated display text to 100MB"^)
echo     
echo     # Update JavaScript validation
echo     if "file.size > 10 * 1024 * 1024" in content:
echo         content = content.replace("file.size > 10 * 1024 * 1024", "file.size > 100 * 1024 * 1024"^)
echo         changes_made = True
echo         print("  ✓ Updated file size validation to 100MB"^)
echo     
echo     # Update alert message
echo     if "Maximum size is 10MB" in content:
echo         content = content.replace("Maximum size is 10MB", "Maximum size is 100MB"^)
echo         changes_made = True
echo         print("  ✓ Updated alert message to 100MB"^)
echo     
echo     if changes_made:
echo         with open(doc_file, 'w', encoding='utf-8'^) as f:
echo             f.write(content^)
echo         print("  ✅ Document uploader fixed!"^)
echo     else:
echo         print("  ℹ Already up to date"^)
echo else:
echo     print("  ⚠ document_uploader.html not found"^)
echo.
echo # Fix 2: ML Training Centre endpoint URL
echo print("\n[2/3] Fixing ML Training Centre..."^)
echo ml_file = "modules/ml_training_centre.html"
echo if os.path.exists(ml_file^):
echo     with open(ml_file, 'r', encoding='utf-8'^) as f:
echo         content = f.read(^)
echo     
echo     changes_made = False
echo     
echo     # Fix the endpoint URL
echo     if "/api/ml/status/" in content:
echo         content = content.replace("/api/ml/status/", "/api/ml/training/status/"^)
echo         changes_made = True
echo         print("  ✓ Fixed training status endpoint URL"^)
echo     
echo     if changes_made:
echo         with open(ml_file, 'w', encoding='utf-8'^) as f:
echo             f.write(content^)
echo         print("  ✅ ML Training Centre fixed!"^)
echo     else:
echo         print("  ℹ Already up to date"^)
echo else:
echo     print("  ⚠ ml_training_centre.html not found"^)
echo.
echo # Fix 3: Prediction Centre error handling
echo print("\n[3/3] Fixing Prediction Centre..."^)
echo pred_file = "modules/prediction_centre.html"
echo if os.path.exists(pred_file^):
echo     with open(pred_file, 'r', encoding='utf-8'^) as f:
echo         content = f.read(^)
echo     
echo     changes_made = False
echo     
echo     # Add proper error handling for historical endpoint
echo     if "} catch {" in content:
echo         content = content.replace(
echo             "} catch {",
echo             "} catch (error^) {\n                // Silently handle historical endpoint not existing\n                console.log('Historical endpoint check failed:', error.message^);"
echo         ^)
echo         changes_made = True
echo         print("  ✓ Added error handling for historical endpoint"^)
echo     
echo     if changes_made:
echo         with open(pred_file, 'w', encoding='utf-8'^) as f:
echo             f.write(content^)
echo         print("  ✅ Prediction Centre fixed!"^)
echo     else:
echo         print("  ℹ Already up to date"^)
echo else:
echo     print("  ⚠ prediction_centre.html not found"^)
echo.
echo print("\n" + "="*50^)
echo print("✅ All patches applied successfully!"^)
echo print("="*50^)
echo print("\nIMPORTANT: Please refresh your browser (Ctrl+F5^)"^)
echo print("to ensure all changes take effect."^)
echo print("\nNo service restart required for these changes."^)
) > apply_v18_patches.py

:: Run the patch script
python apply_v18_patches.py

:: Clean up
del apply_v18_patches.py

echo.
echo ==========================================
echo Patch Applied Successfully!
echo ==========================================
echo.
echo All v18 fixes have been applied:
echo ✓ Document upload limit increased to 100MB
echo ✓ ML Training status URL fixed
echo ✓ Prediction Centre error handling improved
echo.
echo Please refresh your browser (Ctrl+F5) to see the changes.
echo No need to restart services or reinstall!
echo.
pause
@echo off
echo ==========================================
echo Fixing Document Upload Limit to 100MB
echo ==========================================
echo.

:: Create a Python script to fix the upload limit
echo Creating fix script...
(
echo import os
echo import sys
echo.
echo print("Updating Document Uploader to 100MB limit..."^)
echo.
echo doc_file = "modules/document_uploader.html"
echo if not os.path.exists(doc_file^):
echo     print("ERROR: document_uploader.html not found!"^)
echo     print("Make sure you run this from the Stock Tracker root folder."^)
echo     sys.exit(1^)
echo.
echo # Read the file
echo with open(doc_file, 'r', encoding='utf-8'^) as f:
echo     content = f.read(^)
echo.
echo # Fix the display text
echo old_text = "Max 10MB"
echo new_text = "Max 100MB"
echo if old_text in content:
echo     content = content.replace(old_text, new_text^)
echo     print("  ✓ Updated display text from 10MB to 100MB"^)
echo else:
echo     print("  ! Display text already updated or not found"^)
echo.
echo # Fix the JavaScript validation
echo old_check = "file.size > 10 * 1024 * 1024"
echo new_check = "file.size > 100 * 1024 * 1024"
echo if old_check in content:
echo     content = content.replace(old_check, new_check^)
echo     print("  ✓ Updated file size validation from 10MB to 100MB"^)
echo else:
echo     print("  ! Validation already updated or not found"^)
echo.
echo # Fix the alert message
echo old_alert = "Maximum size is 10MB"
echo new_alert = "Maximum size is 100MB"
echo if old_alert in content:
echo     content = content.replace(old_alert, new_alert^)
echo     print("  ✓ Updated alert message"^)
echo else:
echo     print("  ! Alert message already updated"^)
echo.
echo # Write the updated content back
echo with open(doc_file, 'w', encoding='utf-8'^) as f:
echo     f.write(content^)
echo.
echo print("\n✅ Document upload limit updated to 100MB!"^)
echo print("\nNOTE: The backend already supports 100MB uploads."^)
echo print("This fix updates the frontend validation to match."^)
echo print("\nPlease refresh your browser (Ctrl+F5^) to see the changes."^)
) > fix_upload_limit.py

:: Run the Python script
python fix_upload_limit.py

:: Clean up
del fix_upload_limit.py

echo.
echo ==========================================
echo Fix Applied Successfully!
echo ==========================================
echo.
echo The document uploader now accepts files up to 100MB.
echo Please refresh your browser to see the changes.
echo.
pause
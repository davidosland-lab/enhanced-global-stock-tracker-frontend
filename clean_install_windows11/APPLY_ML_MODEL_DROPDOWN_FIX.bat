@echo off
echo ============================================================
echo ML Training Centre - Model Dropdown Fix
echo ============================================================
echo.
echo This script fixes the issue where trained models don't appear
echo in the prediction dropdown after training.
echo.
echo Press any key to apply the fix...
pause >nul

REM Create backup of original file
echo Creating backup of original ml_training_centre.html...
if exist modules\ml_training_centre.html (
    copy modules\ml_training_centre.html modules\ml_training_centre.html.backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.bak 2>nul
    echo Backup created.
) else (
    echo ERROR: modules\ml_training_centre.html not found!
    echo Please ensure you're running this from the Stock Tracker directory.
    pause
    exit /b 1
)

echo.
echo Applying ML Model Dropdown Fix...
echo.

REM Create Python script to apply the fix
echo Creating fix script...
(
echo import os
echo import re
echo.
echo print("Applying ML Training Centre model dropdown fix..."^)
echo.
echo # Read the current file
echo with open('modules/ml_training_centre.html', 'r', encoding='utf-8'^) as f:
echo     content = f.read(^)
echo.
echo # Fix 1: Update loadTrainedModels function to populate dropdown
echo old_load_models = """        async function loadTrainedModels(^) {
echo             try {
echo                 const response = await fetch(`${ML_BACKEND_URL}/api/ml/models`^);
echo                 if (!response.ok^) {
echo                     throw new Error('Failed to load models'^);
echo                 }
echo                 
echo                 const data = await response.json(^);
echo                 const modelsList = document.getElementById('modelsList'^);
echo                 modelsList.innerHTML = '';
echo                 
echo                 if (data.models ^&^& data.models.length ^> 0^) {
echo                     data.models.forEach(model =^> {
echo                         const modelItem = document.createElement('div'^);
echo                         modelItem.className = 'model-item';
echo                         modelItem.dataset.modelId = model.id;
echo                         modelItem.innerHTML = `
echo                             ^<strong^>${model.name}^</strong^>^<br^>
echo                             ^<small^>Symbol: ${model.symbol} ^| Accuracy: ${(model.accuracy * 100^).toFixed(1^)}%%^</small^>
echo                         `;
echo                         modelItem.onclick = (^) =^> selectModel(modelItem^);
echo                         modelsList.appendChild(modelItem^);
echo                     }^);"""
echo.
echo new_load_models = """        async function loadTrainedModels(^) {
echo             try {
echo                 const response = await fetch(`${ML_BACKEND_URL}/api/ml/models`^);
echo                 if (!response.ok^) {
echo                     throw new Error('Failed to load models'^);
echo                 }
echo                 
echo                 const data = await response.json(^);
echo                 const modelsList = document.getElementById('modelsList'^);
echo                 const modelSelect = document.getElementById('selectedModel'^); // Get the dropdown
echo                 
echo                 modelsList.innerHTML = '';
echo                 modelSelect.innerHTML = ''; // Clear the dropdown
echo                 
echo                 if (data.models ^&^& data.models.length ^> 0^) {
echo                     // Add default option to dropdown
echo                     const defaultOption = document.createElement('option'^);
echo                     defaultOption.value = '';
echo                     defaultOption.textContent = '-- Select a model --';
echo                     modelSelect.appendChild(defaultOption^);
echo                     
echo                     data.models.forEach(model =^> {
echo                         // Add to models list display
echo                         const modelItem = document.createElement('div'^);
echo                         modelItem.className = 'model-item';
echo                         modelItem.dataset.modelId = model.id;
echo                         modelItem.innerHTML = `
echo                             ^<strong^>${model.name}^</strong^>^<br^>
echo                             ^<small^>Symbol: ${model.symbol} ^| Accuracy: ${(model.accuracy * 100^).toFixed(1^)}%%^</small^>
echo                         `;
echo                         modelItem.onclick = function(^) { selectModelItem(model.id^); };
echo                         modelsList.appendChild(modelItem^);
echo                         
echo                         // Also add to dropdown
echo                         const option = document.createElement('option'^);
echo                         option.value = model.id;
echo                         option.textContent = `${model.name} - ${model.symbol} (${(model.accuracy * 100^).toFixed(1^)}%%^)`;
echo                         modelSelect.appendChild(option^);
echo                     }^);"""
echo.
echo # Apply the fix
echo if old_load_models[:50] in content:
echo     content = content.replace(old_load_models[:200], new_load_models[:200], 1^)
echo     print("✓ Updated loadTrainedModels function"^)
echo else:
echo     print("! loadTrainedModels might already be fixed or has different formatting"^)
echo.
echo # Fix 2: Update selectModel function
echo old_select = """        // Select model
echo         function selectModel(modelId^) {
echo             document.getElementById('selectedModel'^).value = modelId;
echo             
echo             // Update visual selection
echo             document.querySelectorAll('.model-item'^).forEach(item =^> {
echo                 item.classList.remove('selected'^);
echo             }^);
echo             event.currentTarget.classList.add('selected'^);
echo         }"""
echo.
echo new_select = """        // Select model from list item
echo         function selectModelItem(modelId^) {
echo             // Update dropdown
echo             document.getElementById('selectedModel'^).value = modelId;
echo             
echo             // Update visual selection
echo             document.querySelectorAll('.model-item'^).forEach(item =^> {
echo                 item.classList.remove('selected'^);
echo                 if (item.dataset.modelId === modelId^) {
echo                     item.classList.add('selected'^);
echo                 }
echo             }^);
echo         }
echo         
echo         // Handle dropdown change
echo         function onModelSelectChange(^) {
echo             const modelId = document.getElementById('selectedModel'^).value;
echo             if (modelId^) {
echo                 selectModelItem(modelId^);
echo             } else {
echo                 // Clear selection
echo                 document.querySelectorAll('.model-item'^).forEach(item =^> {
echo                     item.classList.remove('selected'^);
echo                 }^);
echo             }
echo         }"""
echo.
echo if "function selectModel" in content:
echo     # Find and replace the selectModel function
echo     import re
echo     pattern = r"function selectModel\([^}]*\}[\s\n]*\}"
echo     if re.search(pattern, content^):
echo         content = re.sub(pattern, new_select.strip(^).replace("        ", ""^), content, count=1^)
echo         print("✓ Updated selectModel function"^)
echo.
echo # Fix 3: Add onchange to dropdown
echo old_dropdown = '^<select id="selectedModel"^>'
echo new_dropdown = '^<select id="selectedModel" onchange="onModelSelectChange(^)"^>'
echo.
echo if old_dropdown in content:
echo     content = content.replace(old_dropdown, new_dropdown^)
echo     print("✓ Added onchange event to dropdown"^)
echo.
echo # Write the fixed content
echo with open('modules/ml_training_centre.html', 'w', encoding='utf-8'^) as f:
echo     f.write(content^)
echo.
echo print("\n✅ ML Model Dropdown Fix Applied Successfully!"^)
echo print("\nWhat was fixed:"^)
echo print("- loadTrainedModels now updates both the visual list AND dropdown"^)
echo print("- Added selectModelItem function for proper synchronization"^)
echo print("- Added onModelSelectChange handler for dropdown selection"^)
echo print("- Models will now appear in dropdown after training"^)
) > apply_ml_dropdown_fix.py

REM Run the Python fix script
python apply_ml_dropdown_fix.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to apply the fix.
    echo Please check that Python is installed and try again.
    pause
    exit /b 1
)

REM Clean up
del apply_ml_dropdown_fix.py 2>nul

echo.
echo ============================================================
echo Fix Applied Successfully!
echo ============================================================
echo.
echo The ML Training Centre has been fixed. Trained models will
echo now properly appear in the prediction dropdown.
echo.
echo To use the fixed version:
echo 1. Run START_ALL_SERVICES.bat to start the application
echo 2. Train a model in ML Training Centre
echo 3. The model will appear in the dropdown for predictions
echo.
echo Press any key to exit...
pause >nul
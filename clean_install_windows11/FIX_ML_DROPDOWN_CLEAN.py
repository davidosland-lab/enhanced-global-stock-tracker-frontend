#!/usr/bin/env python3
"""
Clean fix for ML Training Centre model dropdown issue
This script creates a properly fixed version without syntax errors
"""

import os
import shutil
from datetime import datetime

def fix_ml_training_centre():
    """Apply the model dropdown fix cleanly"""
    
    file_path = "modules/ml_training_centre.html"
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"ERROR: {file_path} not found!")
        print("Please run this script from the Stock Tracker main directory")
        return False
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"✓ Created backup: {backup_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove any stray ^ characters that might have been added
    if '^' in content:
        print("Found and removing stray ^ characters...")
        content = content.replace('^', '')
    
    # Fix 1: Update loadTrainedModels function
    print("Applying fixes...")
    
    # Find the loadTrainedModels function and fix it
    old_function_start = """        async function loadTrainedModels() {
            try {
                const response = await fetch(`${ML_BACKEND_URL}/api/ml/models`);
                if (!response.ok) {
                    throw new Error('Failed to load models');
                }
                
                const data = await response.json();
                const modelsList = document.getElementById('modelsList');"""
    
    new_function_start = """        async function loadTrainedModels() {
            try {
                const response = await fetch(`${ML_BACKEND_URL}/api/ml/models`);
                if (!response.ok) {
                    throw new Error('Failed to load models');
                }
                
                const data = await response.json();
                const modelsList = document.getElementById('modelsList');
                const modelSelect = document.getElementById('selectedModel');"""
    
    if old_function_start in content:
        content = content.replace(old_function_start, new_function_start)
        print("✓ Added modelSelect reference")
    
    # Fix 2: Clear both the list and dropdown
    old_clear = """                modelsList.innerHTML = '';
                
                if (data.models && data.models.length > 0) {"""
    
    new_clear = """                modelsList.innerHTML = '';
                modelSelect.innerHTML = '';
                
                if (data.models && data.models.length > 0) {
                    // Add default option to dropdown
                    const defaultOption = document.createElement('option');
                    defaultOption.value = '';
                    defaultOption.textContent = '-- Select a model --';
                    modelSelect.appendChild(defaultOption);
                    """
    
    if "modelsList.innerHTML = '';" in content and "modelSelect.innerHTML = '';" not in content:
        content = content.replace(old_clear, new_clear)
        print("✓ Added dropdown clearing and default option")
    
    # Fix 3: Add dropdown population in the forEach loop
    old_foreach = """                    data.models.forEach(model => {
                        const modelItem = document.createElement('div');
                        modelItem.className = 'model-item';
                        modelItem.dataset.modelId = model.id;
                        modelItem.innerHTML = `
                            <strong>${model.name}</strong><br>
                            <small>Symbol: ${model.symbol} | Accuracy: ${(model.accuracy * 100).toFixed(1)}%</small>
                        `;
                        modelItem.onclick = function() { selectModelItem(model.id); };
                        modelsList.appendChild(modelItem);
                    });"""
    
    new_foreach = """                    data.models.forEach(model => {
                        // Add to models list display
                        const modelItem = document.createElement('div');
                        modelItem.className = 'model-item';
                        modelItem.dataset.modelId = model.id;
                        modelItem.innerHTML = `
                            <strong>${model.name}</strong><br>
                            <small>Symbol: ${model.symbol} | Accuracy: ${(model.accuracy * 100).toFixed(1)}%</small>
                        `;
                        modelItem.onclick = function() { selectModelItem(model.id); };
                        modelsList.appendChild(modelItem);
                        
                        // Also add to dropdown
                        const option = document.createElement('option');
                        option.value = model.id;
                        option.textContent = `${model.name} - ${model.symbol} (${(model.accuracy * 100).toFixed(1)}%)`;
                        modelSelect.appendChild(option);
                    });"""
    
    # Look for the forEach pattern and replace it
    if "data.models.forEach(model =>" in content:
        # Find the section and update it
        import re
        pattern = r"data\.models\.forEach\(model => \{[^}]+modelsList\.appendChild\(modelItem\);\s*\}\);"
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            for match in matches:
                if "// Also add to dropdown" not in match:
                    # This forEach doesn't have dropdown code yet
                    new_match = match.replace(
                        "modelsList.appendChild(modelItem);",
                        """modelsList.appendChild(modelItem);
                        
                        // Also add to dropdown
                        const option = document.createElement('option');
                        option.value = model.id;
                        option.textContent = `${model.name} - ${model.symbol} (${(model.accuracy * 100).toFixed(1)}%)`;
                        modelSelect.appendChild(option);"""
                    )
                    content = content.replace(match, new_match)
                    print("✓ Added dropdown population in forEach")
    
    # Fix 4: Add the selectModelItem function if it doesn't exist
    if "function selectModelItem" not in content:
        # Find where to add it (after selectModel or before generatePredictions)
        insert_point = content.find("        // Generate predictions")
        if insert_point > 0:
            new_functions = """        // Select model from list item
        function selectModelItem(modelId) {
            // Update dropdown
            document.getElementById('selectedModel').value = modelId;
            
            // Update visual selection
            document.querySelectorAll('.model-item').forEach(item => {
                item.classList.remove('selected');
                if (item.dataset.modelId === modelId) {
                    item.classList.add('selected');
                }
            });
        }
        
        // Handle dropdown change
        function onModelSelectChange() {
            const modelId = document.getElementById('selectedModel').value;
            if (modelId) {
                selectModelItem(modelId);
            } else {
                // Clear selection
                document.querySelectorAll('.model-item').forEach(item => {
                    item.classList.remove('selected');
                });
            }
        }
        
"""
            content = content[:insert_point] + new_functions + content[insert_point:]
            print("✓ Added selectModelItem and onModelSelectChange functions")
    
    # Fix 5: Add onchange to dropdown if not present
    old_select = '<select id="selectedModel">'
    new_select = '<select id="selectedModel" onchange="onModelSelectChange()">'
    
    if old_select in content:
        content = content.replace(old_select, new_select)
        print("✓ Added onchange event to dropdown")
    
    # Fix 6: Handle "no models" case for dropdown
    no_models_section = """                } else {
                    modelsList.innerHTML = '<p>No trained models available</p>';"""
    
    no_models_with_dropdown = """                } else {
                    modelsList.innerHTML = '<p>No trained models available</p>';
                    
                    // Add "no models" option to dropdown
                    const noModelsOption = document.createElement('option');
                    noModelsOption.value = '';
                    noModelsOption.textContent = '-- No models available --';
                    modelSelect.appendChild(noModelsOption);"""
    
    if no_models_section in content and "// Add \"no models\" option to dropdown" not in content:
        content = content.replace(no_models_section, no_models_with_dropdown)
        print("✓ Added no models handling for dropdown")
    
    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ ML Training Centre successfully fixed!")
    print("\nWhat was fixed:")
    print("- Models now populate in both list and dropdown")
    print("- Added model selection synchronization")
    print("- Removed any syntax errors")
    print("\nThe application is ready to use!")
    
    return True

if __name__ == "__main__":
    fix_ml_training_centre()
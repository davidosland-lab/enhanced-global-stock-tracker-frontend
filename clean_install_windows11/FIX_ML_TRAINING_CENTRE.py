#!/usr/bin/env python3
"""
Fix ML Training Centre undefined ID issue
The frontend expects 'model_id' but backend returns 'training_id'
"""

import os
import re
from datetime import datetime

def fix_ml_training_centre():
    """Fix the undefined training ID issue in ML Training Centre"""
    
    # Fix the ML Training Centre HTML
    ml_centre_path = "modules/ml_training_centre.html"
    
    if not os.path.exists(ml_centre_path):
        print(f"! {ml_centre_path} not found")
        return False
    
    # Backup the file
    backup_path = f"{ml_centre_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(ml_centre_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created backup: {backup_path}")
    
    # Fix 1: Handle both model_id and training_id
    old_code = """                const data = await response.json();
                currentTrainingId = data.model_id;"""
    
    new_code = """                const data = await response.json();
                currentTrainingId = data.training_id || data.model_id || data.id;"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✓ Fixed training ID assignment to handle multiple response formats")
    
    # Fix 2: Add validation before checking status
    old_check = """        // Check training status
        async function checkTrainingStatus(modelId) {
            try {
                const response = await fetch(`${ML_BACKEND_URL}/api/ml/status/${modelId}`);"""
    
    new_check = """        // Check training status
        async function checkTrainingStatus(modelId) {
            // Skip if no valid model ID
            if (!modelId || modelId === 'undefined') {
                console.log('Skipping status check - no valid model ID');
                return;
            }
            
            try {
                const response = await fetch(`${ML_BACKEND_URL}/api/ml/status/${modelId}`);"""
    
    if "async function checkTrainingStatus(modelId)" in content:
        content = re.sub(
            r'async function checkTrainingStatus\(modelId\) \{\s*try \{',
            '''async function checkTrainingStatus(modelId) {
            // Skip if no valid model ID
            if (!modelId || modelId === 'undefined') {
                console.log('Skipping status check - no valid model ID');
                return;
            }
            
            try {''',
            content,
            count=1
        )
        print("✓ Added validation to checkTrainingStatus")
    
    # Fix 3: Improve error handling in interval
    old_interval = """                // Start monitoring training progress
                trainingInterval = setInterval(() => checkTrainingStatus(currentTrainingId), 2000);"""
    
    new_interval = """                // Start monitoring training progress
                if (currentTrainingId && currentTrainingId !== 'undefined') {
                    trainingInterval = setInterval(() => {
                        if (currentTrainingId && currentTrainingId !== 'undefined') {
                            checkTrainingStatus(currentTrainingId);
                        }
                    }, 2000);
                } else {
                    console.error('Invalid training ID received:', currentTrainingId);
                    showAlert('Failed to get training ID from server', 'error');
                    document.getElementById('trainBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                    document.getElementById('trainingProgress').style.display = 'none';
                }"""
    
    if "// Start monitoring training progress" in content:
        content = re.sub(
            r'// Start monitoring training progress\s*\n\s*trainingInterval = setInterval[^;]+;',
            new_interval,
            content
        )
        print("✓ Added validation to training interval")
    
    # Write the fixed content
    with open(ml_centre_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed {ml_centre_path}")
    return True

def update_backend_ml_response():
    """Ensure backend returns consistent response format"""
    
    backend_path = "backend_ml_fixed.py"
    
    if not os.path.exists(backend_path):
        print(f"! {backend_path} not found")
        return False
    
    with open(backend_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure the training endpoint returns both training_id and model_id
    if "@app.post(\"/api/ml/train\")" in content:
        # Find the return statement in the train endpoint
        old_return = """    return {
        "training_id": training_id,
        "status": "started",
        "message": f"Training {request.model_type} model for {request.symbol}"
    }"""
        
        new_return = """    return {
        "training_id": training_id,
        "model_id": training_id,  # Added for compatibility
        "id": training_id,  # Alternative field
        "status": "started",
        "message": f"Training {request.model_type} model for {request.symbol}"
    }"""
        
        if '"model_id": training_id' not in content:
            content = re.sub(
                r'return \{\s*"training_id":\s*training_id,\s*"status":\s*"started"',
                '''return {
        "training_id": training_id,
        "model_id": training_id,  # Added for compatibility
        "id": training_id,  # Alternative field
        "status": "started"''',
                content
            )
            
            with open(backend_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated {backend_path} to return consistent IDs")
            return True
        else:
            print(f"✓ {backend_path} already returns model_id")
    
    return True

def main():
    print("=" * 60)
    print("Fixing ML Training Centre Undefined ID Issue")
    print("=" * 60)
    
    # Change to the correct directory if needed
    if os.path.exists("clean_install_windows11"):
        os.chdir("clean_install_windows11")
    
    # Apply fixes
    success = True
    success = fix_ml_training_centre() and success
    success = update_backend_ml_response() and success
    
    if success:
        print("\n✓ All fixes applied successfully!")
        print("\nThe ML Training Centre will now:")
        print("1. Handle multiple ID formats (training_id, model_id, id)")
        print("2. Skip status checks if ID is undefined")
        print("3. Show proper error messages for invalid IDs")
        print("\nRestart the ML Backend for changes to take effect.")
    else:
        print("\n! Some fixes could not be applied")

if __name__ == "__main__":
    main()
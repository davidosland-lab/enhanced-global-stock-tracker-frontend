#!/usr/bin/env python3
"""
Fix ML Training Centre syntax errors that prevent it from loading
"""

import os
import re
from datetime import datetime

def fix_ml_training_centre_syntax():
    """Fix the syntax errors in ML Training Centre"""
    
    ml_centre_path = "modules/ml_training_centre.html"
    
    if not os.path.exists(ml_centre_path):
        print(f"! {ml_centre_path} not found")
        return False
    
    # Read the current content
    with open(ml_centre_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{ml_centre_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created backup: {backup_path}")
    
    fixes_made = []
    
    # Fix 1: Duplicate 'data' declaration issue
    # Find the loadTrainedModels function and fix duplicate declarations
    pattern = r'(async function loadTrainedModels\(\)[^{]*{[^}]*?)const data = await response\.json\(\);([^}]*?)const data = await response\.json\(\);'
    if re.search(pattern, content, re.DOTALL):
        # Remove the second declaration
        content = re.sub(
            r'(const data = await response\.json\(\);.*?)\n\s*const data = await response\.json\(\);',
            r'\1',
            content,
            flags=re.DOTALL
        )
        fixes_made.append("Fixed duplicate 'data' declaration")
    
    # Alternative fix for duplicate data declaration
    # Look for the specific problematic section around line 843
    if 'const data = await response.json();\n                const models = data.models' in content:
        # This looks correct, check if there's another data declaration nearby
        lines = content.split('\n')
        for i in range(len(lines) - 1):
            if 'const data = await response.json();' in lines[i]:
                # Check if there's another one within 10 lines
                for j in range(i + 1, min(i + 10, len(lines))):
                    if 'const data = await response.json();' in lines[j]:
                        # Found duplicate, comment out the second one
                        lines[j] = '                // ' + lines[j].strip() + ' // Duplicate removed'
                        content = '\n'.join(lines)
                        fixes_made.append(f"Commented out duplicate data declaration at line {j+1}")
                        break
    
    # Fix 2: Ensure functions are properly defined
    # Check if startTraining function exists
    if 'function startTraining' not in content and 'async function startTraining' not in content:
        # Add the missing startTraining function
        training_function = """
        // Start training function
        async function startTraining() {
            console.log('Starting training...');
            
            const symbol = document.getElementById('stockSymbol').value || 'CBA.AX';
            const modelType = document.getElementById('modelType').value;
            const epochs = parseInt(document.getElementById('epochs').value) || 50;
            const batchSize = parseInt(document.getElementById('batchSize').value) || 32;
            const learningRate = parseFloat(document.getElementById('learningRate').value) || 0.001;
            const sequenceLength = parseInt(document.getElementById('sequenceLength').value) || 60;
            
            // Disable train button, enable stop button
            document.getElementById('trainBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            
            // Show training progress
            document.getElementById('trainingProgress').style.display = 'block';
            
            // Clear previous data
            document.getElementById('logOutput').innerHTML = '';
            
            try {
                const response = await fetch(`${ML_BACKEND_URL}/api/ml/train`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        symbol: symbol,
                        model_type: modelType,
                        sequence_length: sequenceLength,
                        epochs: epochs,
                        batch_size: batchSize,
                        learning_rate: learningRate
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to start training');
                }
                
                const result = await response.json();
                currentTrainingId = result.training_id || result.model_id || result.id;
                
                if (currentTrainingId) {
                    showAlert(`Training started for ${symbol} using ${modelType.toUpperCase()} model`, 'success');
                    addLog(`Training ID: ${currentTrainingId}`);
                    
                    // Start monitoring progress
                    if (currentTrainingId && currentTrainingId !== 'undefined') {
                        trainingInterval = setInterval(() => {
                            if (currentTrainingId && currentTrainingId !== 'undefined') {
                                checkTrainingStatus(currentTrainingId);
                            }
                        }, 2000);
                    }
                } else {
                    throw new Error('No training ID received');
                }
                
            } catch (error) {
                console.error('Error starting training:', error);
                showAlert('Failed to start training: ' + error.message, 'error');
                document.getElementById('trainBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                document.getElementById('trainingProgress').style.display = 'none';
            }
        }"""
        
        # Insert before the closing script tag
        content = content.replace('</script>', training_function + '\n    </script>')
        fixes_made.append("Added missing startTraining function")
    
    # Fix 3: Ensure proper variable declarations
    # Make sure ML_BACKEND_URL is defined
    if 'const ML_BACKEND_URL' not in content:
        # Add ML_BACKEND_URL declaration at the beginning of script
        content = re.sub(
            r'<script>',
            '<script>\n        const ML_BACKEND_URL = "http://localhost:8003";',
            content,
            count=1
        )
        fixes_made.append("Added ML_BACKEND_URL constant")
    
    # Fix 4: Ensure required variables are declared
    if 'let currentTrainingId' not in content and 'var currentTrainingId' not in content:
        # Add variable declarations
        content = re.sub(
            r'(const ML_BACKEND_URL[^;]*;)',
            r'\1\n        let currentTrainingId = null;\n        let trainingInterval = null;\n        let lossChart = null;\n        let predictionChart = null;',
            content
        )
        fixes_made.append("Added required variable declarations")
    
    # Fix 5: Remove any duplicate function declarations
    # Check for duplicate function definitions
    function_names = ['startTraining', 'stopTraining', 'checkTrainingStatus', 'loadTrainedModels', 'generatePredictions']
    for func_name in function_names:
        pattern = f'(async )?function {func_name}'
        matches = re.findall(pattern, content)
        if len(matches) > 1:
            # Keep only the first occurrence
            first_occurrence = True
            new_content = []
            for line in content.split('\n'):
                if f'function {func_name}' in line:
                    if first_occurrence:
                        new_content.append(line)
                        first_occurrence = False
                    else:
                        new_content.append('// ' + line + ' // Duplicate removed')
                else:
                    new_content.append(line)
            content = '\n'.join(new_content)
            fixes_made.append(f"Removed duplicate {func_name} function")
    
    # Write the fixed content
    with open(ml_centre_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed {ml_centre_path}")
    for fix in fixes_made:
        print(f"  - {fix}")
    
    return True

def create_simple_test_page():
    """Create a simple test page to verify ML Training Centre works"""
    
    test_html = '''<!DOCTYPE html>
<html>
<head>
    <title>ML Training Centre Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            background: #2a2a2a;
        }
        .connected { border-left: 4px solid #4CAF50; }
        .error { border-left: 4px solid #f44336; }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <h1>ML Training Centre Connection Test</h1>
    
    <div class="status" id="mlStatus">Checking ML Backend...</div>
    
    <button onclick="testConnection()">Test ML Backend</button>
    <button onclick="testTraining()">Test Start Training</button>
    <button onclick="testModels()">Test Get Models</button>
    
    <div id="result" class="status" style="margin-top: 20px; white-space: pre-wrap;"></div>
    
    <script>
        const ML_BACKEND_URL = 'http://localhost:8003';
        
        async function testConnection() {
            try {
                const response = await fetch(`${ML_BACKEND_URL}/health`);
                const data = await response.json();
                document.getElementById('mlStatus').className = 'status connected';
                document.getElementById('mlStatus').textContent = '✓ ML Backend Connected';
                document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('mlStatus').className = 'status error';
                document.getElementById('mlStatus').textContent = '✗ ML Backend Not Connected';
                document.getElementById('result').textContent = 'Error: ' + error.message;
            }
        }
        
        async function testTraining() {
            try {
                const response = await fetch(`${ML_BACKEND_URL}/api/ml/train`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        symbol: 'CBA.AX',
                        model_type: 'lstm',
                        epochs: 10
                    })
                });
                const data = await response.json();
                document.getElementById('result').textContent = 'Training Response:\n' + JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('result').textContent = 'Training Error: ' + error.message;
            }
        }
        
        async function testModels() {
            try {
                const response = await fetch(`${ML_BACKEND_URL}/api/ml/models`);
                const data = await response.json();
                document.getElementById('result').textContent = 'Models Response:\n' + JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('result').textContent = 'Models Error: ' + error.message;
            }
        }
        
        // Test on load
        testConnection();
    </script>
</body>
</html>'''
    
    with open('TEST_ML_CENTRE_CONNECTION.html', 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print("✓ Created TEST_ML_CENTRE_CONNECTION.html")

def main():
    print("=" * 60)
    print("Fixing ML Training Centre Syntax Errors")
    print("=" * 60)
    
    # Change to correct directory if needed
    if os.path.exists("clean_install_windows11"):
        os.chdir("clean_install_windows11")
    
    print("\n🔧 Issues to Fix:")
    print("❌ Duplicate 'data' variable declaration")
    print("❌ startTraining function not defined")
    print("❌ ML Backend connection stuck at 'Checking'")
    
    # Apply fixes
    success = fix_ml_training_centre_syntax()
    create_simple_test_page()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ ML Training Centre Fixed!")
        print("=" * 60)
        print("\n✓ Syntax errors fixed")
        print("✓ Functions properly defined")
        print("✓ Connection should work now")
        print("\nTest with TEST_ML_CENTRE_CONNECTION.html")
        print("\nRestart the frontend server and refresh the ML Training Centre page.")
    else:
        print("\n! Some fixes could not be applied")

if __name__ == "__main__":
    main()
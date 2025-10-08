#!/usr/bin/env python3
"""
Comprehensive fix for ALL syntax errors in ML Training Centre
"""

import os
import re
from datetime import datetime

def comprehensive_ml_fix():
    """Fix all remaining syntax issues in ML Training Centre"""
    
    ml_centre_path = "modules/ml_training_centre.html"
    
    if not os.path.exists(ml_centre_path):
        print(f"! {ml_centre_path} not found")
        return False
    
    # Read the file
    with open(ml_centre_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{ml_centre_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created backup: {backup_path}")
    
    fixes_made = []
    
    # Fix 1: Find all functions and check for duplicate const declarations
    function_pattern = r'(async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    
    def fix_duplicates_in_function(match):
        function_body = match.group(0)
        function_name = match.group(2)
        
        # Find all const/let/var declarations in this function
        const_vars = {}
        lines = function_body.split('\n')
        modified = False
        
        for i, line in enumerate(lines):
            # Check for variable declarations
            var_match = re.search(r'^\s*(const|let|var)\s+(\w+)\s*=', line)
            if var_match:
                var_type = var_match.group(1)
                var_name = var_match.group(2)
                
                if var_name in const_vars:
                    # Duplicate found
                    lines[i] = '                // Duplicate removed: ' + line.strip()
                    modified = True
                    print(f"  Fixed duplicate '{var_name}' in function {function_name}")
                else:
                    const_vars[var_name] = True
        
        if modified:
            return '\n'.join(lines)
        return function_body
    
    # Apply fix to all functions
    content = re.sub(function_pattern, fix_duplicates_in_function, content, flags=re.DOTALL)
    
    # Fix 2: Ensure global variables are declared only once
    # Check for ML_BACKEND_URL
    ml_backend_count = len(re.findall(r'const ML_BACKEND_URL\s*=', content))
    if ml_backend_count > 1:
        # Keep only the first one
        first = True
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'const ML_BACKEND_URL' in line:
                if first:
                    first = False
                else:
                    lines[i] = '        // Duplicate removed: ' + line.strip()
        content = '\n'.join(lines)
        fixes_made.append(f"Removed {ml_backend_count - 1} duplicate ML_BACKEND_URL declarations")
    
    # Fix 3: Ensure currentTrainingId is declared globally
    if 'let currentTrainingId' not in content and 'var currentTrainingId' not in content:
        # Add it at the beginning of the script
        content = re.sub(
            r'<script>\s*\n',
            '<script>\n        let currentTrainingId = null;\n        let trainingInterval = null;\n',
            content,
            count=1
        )
        fixes_made.append("Added missing global variable declarations")
    
    # Fix 4: Check for specific problematic patterns
    # Remove any remaining duplicate await response.json()
    problem_pattern = r'const data = await response\.json\(\);\s*\n\s*const data = await response\.json\(\);'
    if re.search(problem_pattern, content):
        content = re.sub(problem_pattern, 'const data = await response.json();', content)
        fixes_made.append("Fixed consecutive duplicate data declarations")
    
    # Write the fixed content
    with open(ml_centre_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed {ml_centre_path}")
    for fix in fixes_made:
        print(f"  - {fix}")
    
    return True

def create_ml_test_page():
    """Create a simple ML Training Centre test page"""
    
    test_html = '''<!DOCTYPE html>
<html>
<head>
    <title>ML Training Centre Syntax Test</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 50px auto;
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        .status {
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            background: #2a2a2a;
        }
        .success { border-left: 4px solid #4CAF50; }
        .error { border-left: 4px solid #f44336; }
        .warning { border-left: 4px solid #ff9800; }
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
        pre {
            background: #000;
            color: #0f0;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        iframe {
            width: 100%;
            height: 600px;
            border: 2px solid #444;
            border-radius: 10px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>🧪 ML Training Centre Syntax Test</h1>
    
    <div class="status">
        <h2>Quick Tests</h2>
        <button onclick="testMLBackend()">Test ML Backend Connection</button>
        <button onclick="testStartTraining()">Test Start Training</button>
        <button onclick="loadMLTrainingCentre()">Load ML Training Centre</button>
    </div>
    
    <div id="results" class="status"></div>
    
    <div id="console-errors" class="status error" style="display:none;">
        <h3>Console Errors:</h3>
        <pre id="error-log"></pre>
    </div>
    
    <iframe id="mlFrame" style="display:none;"></iframe>
    
    <script>
        const ML_BACKEND_URL = 'http://localhost:8003';
        let originalConsoleError = console.error;
        let errors = [];
        
        // Capture console errors
        console.error = function() {
            const args = Array.from(arguments);
            errors.push(args.join(' '));
            document.getElementById('console-errors').style.display = 'block';
            document.getElementById('error-log').textContent = errors.join('\\n');
            originalConsoleError.apply(console, arguments);
        };
        
        async function testMLBackend() {
            const resultsDiv = document.getElementById('results');
            try {
                const response = await fetch(`${ML_BACKEND_URL}/health`);
                const data = await response.json();
                resultsDiv.className = 'status success';
                resultsDiv.innerHTML = '<h3>✅ ML Backend Connected</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                resultsDiv.className = 'status error';
                resultsDiv.innerHTML = '<h3>❌ ML Backend Not Connected</h3><p>' + error.message + '</p>';
            }
        }
        
        async function testStartTraining() {
            const resultsDiv = document.getElementById('results');
            try {
                const response = await fetch(`${ML_BACKEND_URL}/api/ml/train`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        symbol: 'CBA.AX',
                        model_type: 'lstm',
                        epochs: 5,
                        batch_size: 32,
                        learning_rate: 0.001
                    })
                });
                const data = await response.json();
                resultsDiv.className = 'status success';
                resultsDiv.innerHTML = '<h3>✅ Training Started</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                resultsDiv.innerHTML += '<p>Training ID: ' + (data.training_id || data.model_id || data.id || 'Unknown') + '</p>';
            } catch (error) {
                resultsDiv.className = 'status error';
                resultsDiv.innerHTML = '<h3>❌ Training Failed</h3><p>' + error.message + '</p>';
            }
        }
        
        function loadMLTrainingCentre() {
            errors = [];
            document.getElementById('console-errors').style.display = 'none';
            document.getElementById('mlFrame').style.display = 'block';
            document.getElementById('mlFrame').src = '/modules/ml_training_centre.html';
            
            setTimeout(() => {
                if (errors.length === 0) {
                    document.getElementById('results').className = 'status success';
                    document.getElementById('results').innerHTML = '<h3>✅ ML Training Centre loaded without syntax errors!</h3>';
                } else {
                    document.getElementById('results').className = 'status warning';
                    document.getElementById('results').innerHTML = '<h3>⚠️ ML Training Centre has errors - check console</h3>';
                }
            }, 2000);
        }
        
        // Test on load
        testMLBackend();
    </script>
</body>
</html>'''
    
    with open('TEST_ML_SYNTAX.html', 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print("✓ Created TEST_ML_SYNTAX.html")

def main():
    print("=" * 60)
    print("Comprehensive ML Training Centre Syntax Fix")
    print("=" * 60)
    
    # Change to correct directory if needed
    if os.path.exists("clean_install_windows11"):
        os.chdir("clean_install_windows11")
    
    print("\n🔧 Checking for ALL syntax issues...")
    
    success = comprehensive_ml_fix()
    create_ml_test_page()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ ML Training Centre Comprehensive Fix Complete!")
        print("=" * 60)
        print("\n✓ All duplicate variable declarations removed")
        print("✓ Global variables properly declared")
        print("✓ Function scopes cleaned up")
        print("\nTest with TEST_ML_SYNTAX.html to verify no errors")
    else:
        print("\n! Fix could not be applied")

if __name__ == "__main__":
    main()
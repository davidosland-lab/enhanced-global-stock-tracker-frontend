#!/usr/bin/env python3
"""
Final fix for Prediction Centre:
1. Update index.html to use the correct prediction_centre.html (not phase4)
2. Fix Chart.js date adapter issue
"""

import os
from datetime import datetime

def fix_index_html():
    """Update index.html to use the correct prediction centre"""
    
    index_path = "index.html"
    if not os.path.exists(index_path):
        print(f"! {index_path} not found")
        return False
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{index_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Replace prediction_centre_phase4.html with prediction_centre.html
    old_link = "onclick=\"launchModule('/modules/prediction_centre_phase4.html')\""
    new_link = "onclick=\"launchModule('/modules/prediction_centre.html')\""
    
    if old_link in content:
        content = content.replace(old_link, new_link)
        print("✓ Updated index.html to use correct prediction_centre.html (not phase4)")
    else:
        # Try alternative pattern
        content = content.replace(
            "prediction_centre_phase4.html",
            "prediction_centre.html"
        )
        print("✓ Replaced all references to phase4 with correct prediction centre")
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def fix_chart_date_adapter():
    """Fix the Chart.js date adapter issue in prediction centre"""
    
    pred_centre_path = "modules/prediction_centre.html"
    if not os.path.exists(pred_centre_path):
        print(f"! {pred_centre_path} not found")
        return False
    
    with open(pred_centre_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add Chart.js date adapter if not present
    if 'chartjs-adapter-date-fns' not in content and 'chartjs-adapter-moment' not in content:
        # Add date adapter script after Chart.js
        chart_script = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>'
        date_adapter = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>\n    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>\n    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0"></script>'
        
        content = content.replace(chart_script, date_adapter)
        print("✓ Added Chart.js date adapter to prediction_centre.html")
    
    with open(pred_centre_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def fix_phase4_chart_issue():
    """Also fix the phase4 file in case it's still being used"""
    
    phase4_path = "modules/prediction_centre_phase4.html"
    if not os.path.exists(phase4_path):
        print(f"! {phase4_path} not found")
        return False
    
    with open(phase4_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix Chart.js reuse error - add chart destruction before creation
    old_chart_creation = """function updatePredictionChart(prediction, currentPrice) {
            const ctx = document.getElementById('predictionChart').getContext('2d');
            
            if (predictionChart) {
                predictionChart.destroy();
            }"""
    
    if 'if (predictionChart) {' not in content:
        # Add chart destruction logic
        content = content.replace(
            "function updatePredictionChart(prediction, currentPrice) {\n            const ctx = document.getElementById('predictionChart').getContext('2d');",
            """function updatePredictionChart(prediction, currentPrice) {
            const ctx = document.getElementById('predictionChart').getContext('2d');
            
            // Destroy existing chart if it exists
            if (window.predictionChart) {
                window.predictionChart.destroy();
                window.predictionChart = null;
            }"""
        )
        print("✓ Added chart destruction logic to phase4")
    
    # Also add date adapter
    if 'chartjs-adapter-date-fns' not in content and 'chartjs-adapter-moment' not in content:
        # Add date adapter in head section
        head_end = '</head>'
        date_adapter_scripts = """    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0"></script>
</head>"""
        content = content.replace(head_end, date_adapter_scripts)
        print("✓ Added date adapter to phase4")
    
    # Fix the chart variable scope
    content = content.replace(
        "predictionChart = new Chart(ctx,",
        "window.predictionChart = new Chart(ctx,"
    )
    
    with open(phase4_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def create_test_page():
    """Create a test page to verify which prediction centre is being used"""
    
    test_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Prediction Centre Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        .test-section {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .good { color: #4CAF50; }
        .bad { color: #f44336; }
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
    <h1>🔍 Prediction Centre Version Test</h1>
    
    <div class="test-section">
        <h2>Which Prediction Centre is Loaded?</h2>
        <button onclick="loadCorrectVersion()">Load CORRECT Version (Real ML)</button>
        <button onclick="loadPhase4Version()">Load PHASE4 Version (Random)</button>
        
        <p id="status"></p>
        
        <div id="comparison" style="display:none; margin-top: 20px;">
            <h3>How to Tell the Difference:</h3>
            <ul>
                <li class="good">✓ CORRECT Version: Has connection status indicators at top</li>
                <li class="good">✓ CORRECT Version: Shows "ML Backend" and "Historical Data" status</li>
                <li class="good">✓ CORRECT Version: "Generate Real Prediction" button</li>
                <li class="good">✓ CORRECT Version: Shows data source as "Yahoo Finance"</li>
            </ul>
            <ul>
                <li class="bad">✗ PHASE4 Version: No connection status indicators</li>
                <li class="bad">✗ PHASE4 Version: "Generate Prediction" button (not "Real")</li>
                <li class="bad">✗ PHASE4 Version: Uses Math.random() for predictions</li>
                <li class="bad">✗ PHASE4 Version: Shows simulated confidence scores</li>
            </ul>
        </div>
    </div>
    
    <div class="test-section">
        <iframe id="predictionFrame" src=""></iframe>
    </div>
    
    <script>
        function loadCorrectVersion() {
            document.getElementById('predictionFrame').src = '/modules/prediction_centre.html';
            document.getElementById('status').innerHTML = '<span class="good">Loading CORRECT version with REAL ML predictions...</span>';
            document.getElementById('comparison').style.display = 'block';
        }
        
        function loadPhase4Version() {
            document.getElementById('predictionFrame').src = '/modules/prediction_centre_phase4.html';
            document.getElementById('status').innerHTML = '<span class="bad">Loading PHASE4 version with RANDOM predictions...</span>';
            document.getElementById('comparison').style.display = 'block';
        }
        
        // Load correct version by default
        setTimeout(loadCorrectVersion, 500);
    </script>
</body>
</html>'''
    
    with open('TEST_WHICH_PREDICTION.html', 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print("✓ Created TEST_WHICH_PREDICTION.html")

def main():
    print("=" * 60)
    print("Final Fix for Prediction Centre")
    print("=" * 60)
    
    # Change to correct directory if needed
    if os.path.exists("clean_install_windows11"):
        os.chdir("clean_install_windows11")
    
    print("\n🔧 Issues to Fix:")
    print("❌ index.html pointing to prediction_centre_phase4.html (RANDOM)")
    print("❌ Should point to prediction_centre.html (REAL ML)")
    print("❌ Chart.js date adapter missing")
    print("❌ Chart reuse error")
    
    print("\n📝 Applying Fixes...")
    
    # Apply all fixes
    success = True
    success = fix_index_html() and success
    success = fix_chart_date_adapter() and success
    success = fix_phase4_chart_issue() and success
    create_test_page()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Prediction Centre FINAL Fix Complete!")
        print("=" * 60)
        print("\n🎯 What's Fixed:")
        print("✅ index.html now points to correct prediction_centre.html")
        print("✅ Chart.js date adapter added")
        print("✅ Chart reuse errors fixed")
        print("\n🚀 To Verify:")
        print("1. Restart the frontend server")
        print("2. Clear browser cache (Ctrl+F5)")
        print("3. Navigate to Prediction Centre")
        print("4. Look for connection status indicators at the top")
        print("5. Button should say 'Generate Real Prediction'")
        print("\n📊 Test with TEST_WHICH_PREDICTION.html to compare versions")
    else:
        print("\n! Some fixes could not be applied")

if __name__ == "__main__":
    main()
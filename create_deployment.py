#!/usr/bin/env python3
"""
Create deployment package for ML Stock Prediction System
Includes all fixes and diagnostic tools
"""

import os
import zipfile
import datetime
import shutil

def create_deployment_package():
    """Create a deployment ZIP package with all necessary files"""
    
    # Create deployment directory
    deployment_dir = "ml_stock_prediction_deployment"
    if os.path.exists(deployment_dir):
        shutil.rmtree(deployment_dir)
    os.makedirs(deployment_dir)
    
    # Files to include in deployment
    files_to_include = [
        # Core System Files
        "ml_core_enhanced_production_fixed.py",
        "ml_core_enhanced_interface.html",
        "diagnostic_tool.py",
        
        # Requirements
        "requirements.txt",
        "requirements_full.txt",
        
        # Documentation
        "README_DEPLOYMENT.md",
        "SENTIMENT_IMPACT_ANALYSIS.md",
        
        # Optional Modules
        "comprehensive_sentiment_analyzer.py",
    ]
    
    # Copy files to deployment directory
    print("📦 Creating deployment package...")
    for file in files_to_include:
        if os.path.exists(file):
            shutil.copy2(file, deployment_dir)
            print(f"  ✓ Added {file}")
        else:
            print(f"  ⚠ Warning: {file} not found")
    
    # Create setup script
    setup_script = """#!/bin/bash
# ML Stock Prediction System - Quick Setup Script

echo "🚀 ML Stock Prediction System Setup"
echo "===================================="

# Check Python version
python3 --version

echo ""
echo "📋 Step 1: Running diagnostic tool..."
python3 diagnostic_tool.py

echo ""
echo "📦 Step 2: Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the system:"
echo "  python3 ml_core_enhanced_production_fixed.py"
echo ""
echo "Then open: http://localhost:8000"
"""
    
    with open(os.path.join(deployment_dir, "setup.sh"), "w") as f:
        f.write(setup_script)
    
    # Create Windows setup script
    setup_script_windows = """@echo off
REM ML Stock Prediction System - Quick Setup Script for Windows

echo ML Stock Prediction System Setup
echo ====================================

REM Check Python version
python --version

echo.
echo Step 1: Running diagnostic tool...
python diagnostic_tool.py

echo.
echo Step 2: Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To start the system:
echo   python ml_core_enhanced_production_fixed.py
echo.
echo Then open: http://localhost:8000
pause
"""
    
    with open(os.path.join(deployment_dir, "setup.bat"), "w") as f:
        f.write(setup_script_windows)
    
    print("  ✓ Added setup.sh (Linux/Mac)")
    print("  ✓ Added setup.bat (Windows)")
    
    # Create ZIP file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"ml_stock_prediction_v2_fixed_{timestamp}.zip"
    
    print(f"\n📦 Creating ZIP archive: {zip_filename}")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deployment_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(deployment_dir))
                zipf.write(file_path, arcname)
                print(f"  ✓ Compressed {file}")
    
    # Get file size
    size = os.path.getsize(zip_filename) / 1024  # KB
    if size > 1024:
        size_str = f"{size/1024:.1f} MB"
    else:
        size_str = f"{size:.1f} KB"
    
    print(f"\n✅ Deployment package created successfully!")
    print(f"📦 Package: {zip_filename} ({size_str})")
    print(f"📁 Directory: {deployment_dir}/")
    
    # Create deployment instructions
    instructions = f"""
========================================
🎉 DEPLOYMENT PACKAGE READY
========================================

Package: {zip_filename}
Size: {size_str}
Created: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

TO DEPLOY:
1. Extract {zip_filename}
2. Navigate to {deployment_dir}/
3. Run setup script:
   - Linux/Mac: ./setup.sh
   - Windows: setup.bat
4. Start system: python ml_core_enhanced_production_fixed.py
5. Open browser: http://localhost:8000

WHAT'S FIXED:
✅ makePrediction function defined
✅ StandardScaler shape issues resolved
✅ JSON serialization fixed
✅ Timeout protection added
✅ Sentiment made optional
✅ Port conflicts configurable
✅ Diagnostic tool included
✅ All dependencies updated

RECOMMENDED SETTINGS:
- Start with USE_SENTIMENT = False
- Use Python 3.10 or 3.11
- Ensure 1GB+ RAM available
- Check port 8000 is free

========================================
"""
    
    print(instructions)
    
    # Save instructions to file
    with open("DEPLOYMENT_COMPLETE.txt", "w") as f:
        f.write(instructions)
    
    return zip_filename, deployment_dir

if __name__ == "__main__":
    zip_file, deploy_dir = create_deployment_package()
    print(f"📁 Files are in: {deploy_dir}/")
    print(f"📦 ZIP archive: {zip_file}")
    print("\n🚀 Ready for deployment!")
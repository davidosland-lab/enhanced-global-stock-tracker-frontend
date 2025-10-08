#!/usr/bin/env python3
"""
Create a clean ZIP package for Windows deployment
"""

import zipfile
import os
from datetime import datetime

# Define the files to include in the package
INCLUDE_FILES = [
    # Batch files for Windows
    'START_FIXED_SERVICES.bat',
    'STOP_ALL.bat',
    'INSTALL_REQUIREMENTS.bat',
    'README_WINDOWS.txt',
    
    # Core backend files (fixed versions)
    'backend.py',  # Or backend_working_before_ml_fix.py renamed
    'ml_backend_fixed.py',
    
    # HTML files
    'index.html',
    
    # Module files
    'modules/stock_tracker.html',
    'modules/prediction_centre.html',
    'modules/ml_training_centre.html',
    'modules/historical_data_manager.html',
    'modules/technical_analysis.html',
    'modules/document_uploader.html',
    'modules/global_market_tracker.html',
    'modules/indices_tracker.html',
    'modules/cba_enhanced.html',
    'modules/prediction_centre_phase4.html',
    
    # Market tracking module
    'modules/market-tracking/market_tracker_final.html',
    
    # Analysis modules
    'modules/analysis/document_analyser.html',
    'modules/predictions/prediction_dashboard.html',
]

def create_package():
    """Create the ZIP package"""
    
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"StockTracker_Windows_Fixed_{timestamp}.zip"
    
    print(f"Creating {zip_name}...")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # First ensure we have the right backend.py
        if os.path.exists('backend_working_before_ml_fix.py') and not os.path.exists('backend.py'):
            print("Using backend_working_before_ml_fix.py as backend.py")
            os.system('cp backend_working_before_ml_fix.py backend.py')
        
        for file in INCLUDE_FILES:
            if os.path.exists(file):
                # Add file to zip with its directory structure
                arcname = file.replace('/', '\\')  # Windows paths
                zipf.write(file, arcname)
                print(f"  Added: {file}")
            else:
                # Try alternative locations
                alternatives = [
                    file.replace('.html', '_fixed.html'),
                    file.replace('.html', '_enhanced.html'),
                    file.replace('.html', '_working.html'),
                ]
                added = False
                for alt in alternatives:
                    if os.path.exists(alt):
                        arcname = file.replace('/', '\\')
                        zipf.write(alt, arcname)
                        print(f"  Added: {alt} as {file}")
                        added = True
                        break
                
                if not added:
                    print(f"  Warning: {file} not found")
    
    # Get file size
    size_mb = os.path.getsize(zip_name) / (1024 * 1024)
    print(f"\nPackage created: {zip_name} ({size_mb:.2f} MB)")
    print(f"Ready for Windows deployment!")

if __name__ == "__main__":
    create_package()

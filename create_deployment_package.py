"""
Create Windows 11 Deployment Package

Creates a ZIP file with all necessary files for Windows 11 deployment.
Excludes unnecessary files (git, cache, logs, etc.)
"""

import zipfile
from pathlib import Path
import os
from datetime import datetime

# Base directory
BASE_DIR = Path(__file__).parent

# Output filename
timestamp = datetime.now().strftime('%Y%m%d')
OUTPUT_FILE = BASE_DIR / f'overnight-stock-screener-win11-{timestamp}.zip'

# Files and directories to include
INCLUDE_PATTERNS = [
    # Core modules
    'models/screening/*.py',
    'models/config/*.json',
    'models/lstm/',  # Directory (will be empty initially)
    
    # Scripts
    'scripts/screening/*.py',
    
    # Batch files
    '*.bat',
    
    # Documentation
    'README.md',
    'DEPLOYMENT_GUIDE.md',
    'OVERNIGHT_STOCK_SCREENER_PLAN.md',
    
    # Requirements
    'requirements.txt',
    
    # Empty directories to create
    'reports/morning_reports/',
    'reports/pipeline_state/',
    'logs/screening/',
    'logs/lstm_training/',
]

# Exclusions (files/patterns to skip)
EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '.git',
    '.gitignore',
    'venv',
    '.env',
    '*.log',
    'logs/*.log',
    '*.db',
    'data/',
    '.pytest_cache',
    '.vscode',
    '.idea',
    'create_deployment_package.py',
]

def should_exclude(file_path: str) -> bool:
    """Check if file should be excluded"""
    for pattern in EXCLUDE_PATTERNS:
        if pattern in file_path:
            return True
    return False

def add_directory_recursive(zipf: zipfile.ZipFile, directory: Path, arcname: str = ''):
    """Add directory and all its contents recursively"""
    if not directory.exists():
        return
    
    for item in directory.rglob('*'):
        if item.is_file():
            relative_path = str(item.relative_to(BASE_DIR))
            
            if should_exclude(relative_path):
                continue
            
            arcname_path = relative_path
            print(f"  Adding: {arcname_path}")
            zipf.write(item, arcname_path)

def create_deployment_package():
    """Create the deployment ZIP file"""
    print("="*80)
    print("CREATING WINDOWS 11 DEPLOYMENT PACKAGE")
    print("="*80)
    print()
    
    with zipfile.ZipFile(OUTPUT_FILE, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add specific files and directories
        print("Adding core modules...")
        
        # Models - screening
        models_screening = BASE_DIR / 'models' / 'screening'
        if models_screening.exists():
            for py_file in models_screening.glob('*.py'):
                if should_exclude(str(py_file.relative_to(BASE_DIR))):
                    continue
                arcname = str(py_file.relative_to(BASE_DIR))
                print(f"  Adding: {arcname}")
                zipf.write(py_file, arcname)
        
        # Models - config
        models_config = BASE_DIR / 'models' / 'config'
        if models_config.exists():
            for json_file in models_config.glob('*.json'):
                arcname = str(json_file.relative_to(BASE_DIR))
                print(f"  Adding: {arcname}")
                zipf.write(json_file, arcname)
        
        # Create empty LSTM directory
        print("\nCreating directory structure...")
        zipf.writestr('models/lstm/.gitkeep', '')
        zipf.writestr('reports/morning_reports/.gitkeep', '')
        zipf.writestr('reports/pipeline_state/.gitkeep', '')
        zipf.writestr('logs/screening/.gitkeep', '')
        zipf.writestr('logs/lstm_training/.gitkeep', '')
        
        # Scripts
        print("\nAdding test scripts...")
        scripts_screening = BASE_DIR / 'scripts' / 'screening'
        if scripts_screening.exists():
            for py_file in scripts_screening.glob('*.py'):
                arcname = str(py_file.relative_to(BASE_DIR))
                print(f"  Adding: {arcname}")
                zipf.write(py_file, arcname)
        
        # Batch files
        print("\nAdding batch files...")
        for bat_file in BASE_DIR.glob('*.bat'):
            arcname = str(bat_file.relative_to(BASE_DIR))
            print(f"  Adding: {arcname}")
            zipf.write(bat_file, arcname)
        
        # Documentation
        print("\nAdding documentation...")
        docs = ['README.md', 'DEPLOYMENT_GUIDE.md', 'OVERNIGHT_STOCK_SCREENER_PLAN.md']
        for doc in docs:
            doc_path = BASE_DIR / doc
            if doc_path.exists():
                print(f"  Adding: {doc}")
                zipf.write(doc_path, doc)
        
        # Requirements
        print("\nAdding requirements...")
        req_file = BASE_DIR / 'requirements.txt'
        if req_file.exists():
            print(f"  Adding: requirements.txt")
            zipf.write(req_file, 'requirements.txt')
        
        # Create README for deployment
        print("\nCreating deployment README...")
        readme_content = """# Overnight Stock Screener - Windows 11 Package

## Quick Start

1. Extract this ZIP to a folder (e.g., C:\\overnight-stock-screener\\)
2. Install Python 3.9+ from python.org
3. Open Command Prompt in the extracted folder
4. Run: python -m venv venv
5. Run: venv\\Scripts\\activate
6. Run: pip install -r requirements.txt
7. Test: RUN_OVERNIGHT_SCREENER_TEST.bat

## Full Documentation

See DEPLOYMENT_GUIDE.md for complete setup instructions.

## Contents

- models/           - Core screening modules
- scripts/          - Test and utility scripts
- *.bat             - Windows batch scripts
- requirements.txt  - Python dependencies
- DEPLOYMENT_GUIDE.md - Full deployment guide

## Support

Check logs/ directory for execution logs.
Run CHECK_SCREENER_STATUS.bat for system status.

## Version

Phase 3 Complete - Full Automation with Email Notifications and LSTM Training
Date: """ + datetime.now().strftime('%Y-%m-%d') + """
"""
        zipf.writestr('README_DEPLOYMENT.txt', readme_content)
    
    print("\n" + "="*80)
    print("PACKAGE CREATED SUCCESSFULLY")
    print("="*80)
    print(f"Output: {OUTPUT_FILE}")
    print(f"Size: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    print("Next Steps:")
    print("1. Transfer ZIP to Windows 11 machine")
    print("2. Extract to desired location")
    print("3. Follow DEPLOYMENT_GUIDE.md instructions")
    print("="*80)

if __name__ == '__main__':
    try:
        create_deployment_package()
    except Exception as e:
        print(f"\n❌ Error creating package: {str(e)}")
        import traceback
        traceback.print_exc()

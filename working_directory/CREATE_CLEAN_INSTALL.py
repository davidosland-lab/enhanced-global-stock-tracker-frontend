#!/usr/bin/env python3
"""
Create Complete Clean Installation Package
Version: v1.3.15.45 FINAL
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_clean_install():
    """Create complete clean installation package"""
    
    print("="*80)
    print("Creating Complete Clean Installation Package v1.3.15.45 FINAL")
    print("="*80)
    print()
    
    # Source and destination
    source_dir = Path('complete_backend_clean_install_v1.3.15')
    output_dir = Path('COMPLETE_SYSTEM_v1.3.15.45_FINAL')
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return False
    
    # Remove old output if exists
    if output_dir.exists():
        print(f"🗑️  Removing old package: {output_dir}")
        shutil.rmtree(output_dir)
    
    # Create output directory
    print(f"📁 Creating package directory: {output_dir}")
    output_dir.mkdir(parents=True)
    
    # Define what to include
    include_patterns = {
        # Core Python files
        '*.py': 'Python scripts',
        
        # Models directory
        'models/**/*.py': 'Model files',
        'models/**/*.json': 'Model configs',
        
        # ML Pipeline
        'ml_pipeline/**/*.py': 'ML Pipeline',
        
        # FinBERT v4.4.4
        'finbert_v4.4.4/**/*': 'FinBERT model',
        
        # Config files
        '*.json': 'Config files',
        '*.env.example': 'Environment templates',
        'requirements.txt': 'Dependencies',
        
        # Documentation
        '*.md': 'Documentation',
        
        # Batch files
        '*.bat': 'Windows scripts',
        '*.sh': 'Unix scripts',
        
        # Reports directory (empty structure)
        'reports/': 'Reports directory',
        'logs/': 'Logs directory',
        'data/': 'Data directory',
    }
    
    # Exclude patterns
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.git',
        '.gitignore',
        'venv',
        '*.log',
        '*.backup',
        '*.backup_hotfix',
        'backup_*',
        '*.tmp',
        '*.swp',
    ]
    
    print()
    print("📋 Copying files...")
    print()
    
    copied_count = 0
    
    # Copy all Python files
    for py_file in source_dir.rglob('*.py'):
        # Skip excluded
        if any(excl in str(py_file) for excl in exclude_patterns):
            continue
        
        rel_path = py_file.relative_to(source_dir)
        dest_path = output_dir / rel_path
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(py_file, dest_path)
        copied_count += 1
        if copied_count % 10 == 0:
            print(f"   Copied {copied_count} files...")
    
    # Copy models directory
    models_src = source_dir / 'models'
    if models_src.exists():
        models_dst = output_dir / 'models'
        shutil.copytree(models_src, models_dst, 
                       ignore=shutil.ignore_patterns(*exclude_patterns),
                       dirs_exist_ok=True)
        print(f"   ✅ Copied models directory")
    
    # Copy ml_pipeline directory
    ml_src = source_dir / 'ml_pipeline'
    if ml_src.exists():
        ml_dst = output_dir / 'ml_pipeline'
        shutil.copytree(ml_src, ml_dst,
                       ignore=shutil.ignore_patterns(*exclude_patterns),
                       dirs_exist_ok=True)
        print(f"   ✅ Copied ml_pipeline directory")
    
    # Copy finbert_v4.4.4 if exists
    finbert_src = source_dir / 'finbert_v4.4.4'
    if finbert_src.exists():
        finbert_dst = output_dir / 'finbert_v4.4.4'
        shutil.copytree(finbert_src, finbert_dst,
                       ignore=shutil.ignore_patterns(*exclude_patterns),
                       dirs_exist_ok=True)
        print(f"   ✅ Copied finbert_v4.4.4 directory")
    
    # Copy config and doc files
    for pattern in ['*.md', '*.bat', '*.sh', '*.json', '*.txt', '.env.example']:
        for file in source_dir.glob(pattern):
            if file.is_file() and not any(excl in str(file) for excl in exclude_patterns):
                shutil.copy2(file, output_dir / file.name)
                copied_count += 1
    
    # Create empty directories
    for dir_name in ['reports', 'reports/screening', 'logs', 'data', 'state']:
        (output_dir / dir_name).mkdir(parents=True, exist_ok=True)
        (output_dir / dir_name / '.gitkeep').touch()
    
    print(f"   ✅ Total files copied: {copied_count}")
    print()
    
    # Create requirements.txt with specific versions
    print("📄 Creating requirements.txt...")
    requirements = output_dir / 'requirements.txt'
    requirements.write_text("""# COMPLETE SYSTEM v1.3.15.45 FINAL - Python Dependencies

# Core ML/Data Science
transformers>=4.30.0
torch>=2.0.0
pandas>=2.0.0
numpy>=1.24.0

# Financial Data
yfinance>=0.2.28
yahooquery>=2.3.0

# News & Sentiment
feedparser>=6.0.10
beautifulsoup4>=4.12.0
requests>=2.31.0

# Dashboard
dash>=2.14.0
plotly>=5.17.0

# Utilities
python-dateutil>=2.8.2
pytz>=2023.3
""")
    print(f"   ✅ requirements.txt created")
    print()
    
    # Create comprehensive installer
    print("🔧 Creating installer...")
    create_complete_installer(output_dir)
    print(f"   ✅ INSTALL.bat created")
    print()
    
    # Create README
    print("📖 Creating README...")
    create_readme(output_dir)
    print(f"   ✅ README.md created")
    print()
    
    # Create ZIP package
    print("📦 Creating ZIP package...")
    zip_name = f"{output_dir}.zip"
    if Path(zip_name).exists():
        Path(zip_name).unlink()
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in output_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(output_dir.parent)
                zipf.write(file, arcname)
    
    zip_size = Path(zip_name).stat().st_size / (1024 * 1024)  # MB
    print(f"   ✅ Created: {zip_name} ({zip_size:.1f} MB)")
    print()
    
    # Summary
    print("="*80)
    print("✅ COMPLETE CLEAN INSTALLATION PACKAGE CREATED")
    print("="*80)
    print()
    print(f"📦 Package: {zip_name}")
    print(f"📁 Directory: {output_dir}")
    print(f"📊 Size: {zip_size:.1f} MB")
    print(f"📝 Files: {copied_count}")
    print()
    print("📋 Contents:")
    print("   ✅ All Python source files")
    print("   ✅ Models and ML pipeline")
    print("   ✅ FinBERT v4.4.4 integration")
    print("   ✅ Dashboard and coordinator")
    print("   ✅ Sentiment integration (fixed)")
    print("   ✅ Complete documentation")
    print("   ✅ Automatic installer")
    print("   ✅ requirements.txt")
    print()
    print("🚀 Ready to deploy!")
    print()
    
    return True


def create_complete_installer(output_dir):
    """Create comprehensive installer"""
    
    installer = output_dir / 'INSTALL.bat'
    installer.write_text(r"""@echo off
REM ==============================================================================
REM COMPLETE SYSTEM v1.3.15.45 FINAL - Clean Installation
REM ==============================================================================

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo          COMPLETE REGIME TRADING SYSTEM v1.3.15.45 FINAL
echo                    Clean Installation Script
echo ================================================================================
echo.

REM Check Python
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    echo.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo   - Python %PYTHON_VER% found
echo.

REM Create virtual environment
echo [2/8] Creating virtual environment...
if exist "venv" (
    echo   - Virtual environment already exists
    set /p RECREATE="   Recreate? (Y/N): "
    if /i "!RECREATE!"=="Y" (
        echo   - Removing old venv...
        rmdir /S /Q venv
        python -m venv venv
        echo   - New venv created
    )
) else (
    python -m venv venv
    echo   - Virtual environment created
)
echo.

REM Activate venv
echo [3/8] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo   - Virtual environment activated
echo.

REM Upgrade pip
echo [4/8] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo   - pip upgraded
echo.

REM Install PyTorch (CPU version - compatible)
echo [5/8] Installing PyTorch (CPU version)...
echo   - This ensures compatibility and avoids DLL conflicts
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo   - WARNING: CPU version failed, trying default
    python -m pip install torch torchvision
)
echo   - PyTorch installed
echo.

REM Install other dependencies
echo [6/8] Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo   - All dependencies installed
echo.

REM Download FinBERT model
echo [7/8] Downloading FinBERT model...
echo   - This may take 2-5 minutes (~500MB download)
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('  - Downloading tokenizer...'); AutoTokenizer.from_pretrained('ProsusAI/finbert'); print('  - Downloading model...'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); print('  - FinBERT model ready')"
if errorlevel 1 (
    echo.
    echo   WARNING: FinBERT download encountered an issue
    echo   The model will download automatically on first use
    echo.
    timeout /t 3
) else (
    echo   - FinBERT model cached successfully
)
echo.

REM Clear cache
echo [8/8] Clearing Python cache...
del /S /Q __pycache__\*.pyc 2>nul
del /S /Q models\screening\__pycache__\*.pyc 2>nul
echo   - Cache cleared
echo.

REM Installation complete
echo.
echo ================================================================================
echo                      INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo Virtual environment: venv\
echo Python version: %PYTHON_VER%
echo.
echo ================================================================================
echo                           QUICK START
echo ================================================================================
echo.
echo 1. Activate virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Run AU overnight pipeline:
echo    python run_au_pipeline_v1.3.13.py --full-scan --capital 100000
echo.
echo 3. Start trading dashboard:
echo    python unified_trading_dashboard.py
echo.
echo 4. Open browser to:
echo    http://localhost:8050
echo.
echo ================================================================================
echo                         IMPORTANT NOTES
echo ================================================================================
echo.
echo - ALWAYS activate virtual environment before running scripts
echo - Your prompt will show (venv) when activated
echo - To deactivate: type 'deactivate'
echo.
echo Features:
echo   - FinBERT v4.4.4 sentiment analysis
echo   - Trading gates (BLOCK/REDUCE/CAUTION/ALLOW)
echo   - Unified dashboard with sentiment panel
echo   - Multi-market support (AU/US/UK)
echo   - Paper trading coordinator
echo.
echo ================================================================================
echo.
echo Installation complete! Press any key to exit...
pause >nul
""", encoding='utf-8')
    
    # Make executable
    installer.chmod(0o755)


def create_readme(output_dir):
    """Create comprehensive README"""
    
    readme = output_dir / 'README.md'
    readme.write_text(r"""# Complete Regime Trading System v1.3.15.45 FINAL

## 🚀 Clean Installation Package

This is the **complete, clean installation** of the Regime Trading System with FinBERT v4.4.4 sentiment integration.

## ✨ Features

- ✅ **FinBERT v4.4.4 Sentiment Analysis** - AI-powered market sentiment
- ✅ **Trading Gates** - Automatic position sizing based on sentiment
- ✅ **Unified Dashboard** - Real-time monitoring and control
- ✅ **Multi-Market Support** - AU, US, UK markets
- ✅ **Paper Trading** - Test strategies without risk
- ✅ **Overnight Pipelines** - Automated market analysis

## 📦 What's Included

- Complete Python source code
- FinBERT v4.4.4 integration
- Sentiment analysis system
- Unified trading dashboard
- Paper trading coordinator
- Overnight pipeline scripts
- ML models and screening tools
- Comprehensive documentation
- Automatic installer

## 🔧 Installation (Windows)

### Step 1: Extract Package

Extract the ZIP file to your desired location:
```
C:\Users\david\Regime_trading\
```

### Step 2: Run Installer

```cmd
cd COMPLETE_SYSTEM_v1.3.15.45_FINAL
INSTALL.bat
```

The installer will:
1. Check Python installation
2. Create virtual environment
3. Install PyTorch (CPU version - compatible)
4. Install all dependencies
5. Download FinBERT model (~500MB)
6. Set up directory structure

**Installation time**: 5-10 minutes (depending on internet speed)

### Step 3: Activate Environment

```cmd
venv\Scripts\activate
```

Your prompt will show `(venv)` when activated.

## 🚀 Quick Start

### 1. Run Overnight Pipeline

```cmd
python run_au_pipeline_v1.3.13.py --full-scan --capital 100000
```

This will:
- Scan AU market for opportunities
- Analyze sentiment with FinBERT
- Generate morning report
- Save results to `reports/screening/`

### 2. Start Dashboard

```cmd
python unified_trading_dashboard.py
```

Open browser to: **http://localhost:8050**

The dashboard displays:
- **FinBERT Sentiment Panel** - Real-time sentiment breakdown
- **Trading Gates** - Position sizing based on sentiment
- **Market Status** - Open/Closed status for all markets
- **Portfolio Overview** - Current positions and P&L
- **Recent Decisions** - Trade history and signals

### 3. Run Paper Trading

```cmd
python paper_trading_coordinator.py
```

This will:
- Monitor morning reports
- Execute trades based on signals
- Respect sentiment gates
- Track portfolio performance

## 📊 Trading Gates

The system uses sentiment-based trading gates:

| Gate | Sentiment | Position Size | Action |
|------|-----------|---------------|--------|
| **BLOCK** | Negative > 50% | 0.0x | NO TRADES |
| **REDUCE** | Negative 40-50% | 0.5x | Half positions |
| **CAUTION** | Neutral 30-40% | 0.8x | Reduced positions |
| **ALLOW** | Normal | 1.0x | Normal trading |
| **ALLOW+** | Positive > 60% | 1.2x | Boosted positions |

**Example**:
- Morning sentiment: 65% Negative
- Gate: BLOCK (0.0x)
- Result: **NO TRADES** (system protects capital)

## 📁 Directory Structure

```
COMPLETE_SYSTEM_v1.3.15.45_FINAL/
├── INSTALL.bat                      # Automatic installer
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── unified_trading_dashboard.py     # Main dashboard
├── paper_trading_coordinator.py     # Trading coordinator
├── sentiment_integration.py         # FinBERT integration
├── run_au_pipeline_v1.3.13.py      # AU overnight pipeline
├── run_uk_pipeline_v1.3.13.py      # UK overnight pipeline
├── run_us_pipeline.py               # US overnight pipeline
├── models/
│   └── screening/
│       ├── overnight_pipeline.py    # Core pipeline
│       ├── finbert_bridge.py        # FinBERT bridge
│       └── batch_predictor.py       # Predictions
├── ml_pipeline/                     # ML components
├── finbert_v4.4.4/                  # FinBERT model files
├── reports/                         # Generated reports
│   └── screening/                   # Morning reports
├── logs/                            # Log files
└── venv/                            # Virtual environment (created by installer)
```

## 🔍 Verification

### Check FinBERT Integration

```cmd
python -c "from sentiment_integration import IntegratedSentimentAnalyzer; analyzer = IntegratedSentimentAnalyzer(); print('✅ FinBERT integration working')"
```

### Check Dashboard Import

```cmd
python -c "import unified_trading_dashboard; print('✅ Dashboard ready')"
```

### Run Test Suite

```cmd
python test_finbert_integration.py
```

Expected output:
```
TEST 1: FinBERT Bridge ✅ PASSED
TEST 2: Sentiment Integration ✅ PASSED
TEST 3: Paper Trading Coordinator ✅ PASSED
TEST 4: Dashboard Integration ✅ PASSED
TEST 5: Overnight Pipeline ✅ PASSED
TEST 6: Morning Report Format ✅ PASSED

ALL TESTS PASSED (6/6) ✅
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# API Keys (optional)
ALPHA_VANTAGE_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here

# Trading Parameters
INITIAL_CAPITAL=100000
MAX_POSITION_SIZE=0.1
RISK_PER_TRADE=0.02

# Dashboard
DASHBOARD_PORT=8050
DASHBOARD_HOST=0.0.0.0
```

### Stock Symbols

Edit symbol lists in respective pipeline files:
- AU market: `run_au_pipeline_v1.3.13.py`
- US market: `run_us_pipeline.py`
- UK market: `run_uk_pipeline_v1.3.13.py`

## 🐛 Troubleshooting

### Issue: "Python not found"

**Solution**: Install Python 3.8 or higher from https://www.python.org/downloads/

### Issue: "Virtual environment activation failed"

**Solution**: Run as Administrator or check Python installation

### Issue: "PyTorch/torchvision error"

**Solution**: The installer uses CPU version to avoid conflicts. If you still see errors:

```cmd
venv\Scripts\activate
pip uninstall torch torchvision -y
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Issue: "FinBERT model download failed"

**Solution**: The model will download automatically on first use. Or manually:

```cmd
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('ProsusAI/finbert'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert')"
```

### Issue: "Dashboard stuck on 'FinBERT data loading...'"

**Solution**: This was fixed in v1.3.15.45.1. Ensure you're using the latest version.

### Issue: "ImportError: cannot import name 'SentimentIntegration'"

**Solution**: This was fixed. The correct class is `IntegratedSentimentAnalyzer`.

## 📚 Documentation

- `COMPLETE_INSTALLATION_GUIDE.md` - Detailed installation guide
- `FINBERT_SENTIMENT_INTEGRATION_v1.3.15.45.md` - FinBERT integration details
- `AU_PIPELINE_INTEGRATION_GUIDE.md` - Pipeline usage guide
- `DEPLOYMENT_README.md` - Production deployment guide

## 🆘 Support

### Common Commands

```cmd
# Activate environment (always do this first!)
venv\Scripts\activate

# Check Python version
python --version

# List installed packages
pip list

# Update dependencies
pip install -r requirements.txt --upgrade

# Clear Python cache
del /S /Q __pycache__\*.pyc

# Deactivate environment
deactivate
```

### Directory Check

```cmd
# Verify installation
dir models\screening\*.py
dir reports\screening\
dir logs\
```

## 🎯 System Requirements

- **OS**: Windows 10/11 (or Linux/Mac with modifications)
- **Python**: 3.8 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 5GB free space
- **Internet**: Required for initial setup and market data

## 📝 Version History

- **v1.3.15.45 FINAL** (2026-01-29)
  - Complete clean installation package
  - Fixed dashboard ImportError
  - Improved installer with PyTorch CPU version
  - Enhanced error handling
  - Comprehensive documentation

- **v1.3.15.45** (2026-01-28)
  - FinBERT v4.4.4 integration
  - Trading sentiment gates
  - Dashboard FinBERT panel
  - Multi-component sentiment analysis

## 📄 License

Copyright © 2026 Regime Trading System
All rights reserved.

## 🎉 Ready to Trade!

Your complete trading system is now installed and ready to use.

Remember:
1. **Always activate the virtual environment** before running scripts
2. **Run overnight pipeline** before market open
3. **Monitor the dashboard** during trading hours
4. **Respect sentiment gates** - they protect your capital!

Happy Trading! 🚀
""", encoding='utf-8')


if __name__ == '__main__':
    import sys
    success = create_clean_install()
    sys.exit(0 if success else 1)

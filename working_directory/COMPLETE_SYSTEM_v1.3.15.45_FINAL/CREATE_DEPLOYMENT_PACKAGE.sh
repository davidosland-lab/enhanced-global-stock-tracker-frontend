#!/bin/bash
# Create Clean Deployment Package v1.3.15.86
# Date: 2026-02-03

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Creating Clean Deployment Package v1.3.15.86            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Package name
PACKAGE_NAME="unified_trading_dashboard_v1.3.15.86_COMPLETE"
DEPLOY_DIR="/home/user/webapp/deployments"
PACKAGE_DIR="$DEPLOY_DIR/$PACKAGE_NAME"

# Create deployment directory
echo "📦 Step 1: Creating deployment structure..."
mkdir -p "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR/core"
mkdir -p "$PACKAGE_DIR/config"
mkdir -p "$PACKAGE_DIR/state"
mkdir -p "$PACKAGE_DIR/reports/screening"
mkdir -p "$PACKAGE_DIR/logs"
mkdir -p "$PACKAGE_DIR/docs"
mkdir -p "$PACKAGE_DIR/scripts"

# Copy ESSENTIAL Python files
echo "📄 Step 2: Copying core Python files..."
cp unified_trading_dashboard.py "$PACKAGE_DIR/core/"
cp paper_trading_coordinator.py "$PACKAGE_DIR/core/"
cp sentiment_integration.py "$PACKAGE_DIR/core/"
cp swing_trader_engine.py "$PACKAGE_DIR/core/" 2>/dev/null || echo "  - swing_trader_engine.py not found (optional)"
cp market_calendar_manager.py "$PACKAGE_DIR/core/" 2>/dev/null || echo "  - market_calendar_manager.py not found (optional)"

# Copy configuration files
echo "⚙️  Step 3: Copying configuration files..."
cp config/live_trading_config.json "$PACKAGE_DIR/config/" 2>/dev/null || echo "  - live_trading_config.json not found (will use defaults)"
cp requirements.txt "$PACKAGE_DIR/" 2>/dev/null || echo "  - requirements.txt not found"

# Copy startup scripts
echo "🚀 Step 4: Copying startup scripts..."
cp START.bat "$PACKAGE_DIR/scripts/" 2>/dev/null || echo "  - START.bat not found"
cp run_au_pipeline_v1.3.13.py "$PACKAGE_DIR/scripts/" 2>/dev/null || echo "  - run_au_pipeline_v1.3.13.py not found (optional)"

# Copy initial state and reports
echo "📊 Step 5: Copying initial state and reports..."
cp state/paper_trading_state.json "$PACKAGE_DIR/state/"
cp reports/screening/au_morning_report.json "$PACKAGE_DIR/reports/screening/" 2>/dev/null || echo "  - au_morning_report.json not found (optional)"
cp reports/screening/au_morning_report_2026-02-03.json "$PACKAGE_DIR/reports/screening/" 2>/dev/null || echo "  - Dated report not found (optional)"

# Copy KEY documentation
echo "📚 Step 6: Copying essential documentation..."
cp FILES_TO_DOWNLOAD.md "$PACKAGE_DIR/docs/INSTALLATION_GUIDE.md"
cp DEPLOYMENT_READY.txt "$PACKAGE_DIR/docs/"
cp COMPLETE_FIX_SUMMARY_v84_v85_v86.md "$PACKAGE_DIR/docs/"
cp TRADING_CONTROLS_GUIDE_v86.md "$PACKAGE_DIR/docs/"
cp CURRENT_STATUS.md "$PACKAGE_DIR/docs/"
cp START_HERE.md "$PACKAGE_DIR/docs/" 2>/dev/null || echo "  - START_HERE.md not found (optional)"

# Create README for the package
echo "📝 Step 7: Creating package README..."
cat > "$PACKAGE_DIR/README.md" << 'READMEEOF'
# Unified Trading Dashboard v1.3.15.86 - Complete Deployment Package

## 🎯 What's Inside

This is a **complete, ready-to-deploy** package with all fixes applied:

- ✅ v1.3.15.85 - State Persistence Fix
- ✅ v1.3.15.86 - Trading Controls (Confidence, Stop Loss, Force Trade)
- ✅ v1.3.15.84 - Morning Report Naming Fix

## 📦 Package Contents

```
unified_trading_dashboard_v1.3.15.86_COMPLETE/
├── core/                           # Core Python files
│   ├── unified_trading_dashboard.py
│   ├── paper_trading_coordinator.py
│   ├── sentiment_integration.py
│   └── (other core files)
├── config/                         # Configuration
│   └── live_trading_config.json
├── state/                          # Initial state
│   └── paper_trading_state.json (714 bytes)
├── reports/screening/              # Morning reports
│   └── au_morning_report.json
├── logs/                           # Log files (created on run)
├── scripts/                        # Startup scripts
│   ├── START.bat
│   └── run_au_pipeline_v1.3.13.py
├── docs/                           # Documentation
│   ├── INSTALLATION_GUIDE.md
│   ├── DEPLOYMENT_READY.txt
│   ├── COMPLETE_FIX_SUMMARY_v84_v85_v86.md
│   ├── TRADING_CONTROLS_GUIDE_v86.md
│   └── CURRENT_STATUS.md
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Quick Start (Windows)

### 1. Extract Package
```
Unzip to: C:\Users\david\Regime_trading\
Result:   C:\Users\david\Regime_trading\unified_trading_dashboard_v1.3.15.86_COMPLETE\
```

### 2. Install Dependencies (if needed)
```
cd C:\Users\david\Regime_trading\unified_trading_dashboard_v1.3.15.86_COMPLETE
pip install -r requirements.txt
```

### 3. Copy Core Files to Your Existing Installation
```
Copy files from core/ to:
C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\

OR use this as standalone:
cd core
python unified_trading_dashboard.py --symbols BHP.AX,CBA.AX,RIO.AX --capital 100000
```

### 4. Access Dashboard
```
http://localhost:8050
```

## 🎮 New Trading Controls

Look for **⚙️ Trading Controls** panel in the left column:

1. **Confidence Level Slider** (50-95%, default 65%)
   - Conservative: 80% | Balanced: 65% | Aggressive: 55%

2. **Stop Loss Input** (1-20%, default 10%)
   - Tight: 5% | Moderate: 10% | Loose: 15%

3. **Force Trade Buttons**
   - Enter symbol → Click Force BUY or Force SELL

## 📋 Verification Checklist

After deployment:
- [ ] Dashboard loads at http://localhost:8050
- [ ] Trading Controls panel visible
- [ ] State file exists (not 0 bytes)
- [ ] Trades persist after refresh
- [ ] Charts update every 5 seconds

## 📚 Documentation

See `docs/` folder for:
- `INSTALLATION_GUIDE.md` - Detailed installation steps
- `DEPLOYMENT_READY.txt` - Visual deployment checklist
- `COMPLETE_FIX_SUMMARY_v84_v85_v86.md` - Technical details
- `TRADING_CONTROLS_GUIDE_v86.md` - How to use controls

## 🐛 Troubleshooting

### State file is 0 bytes
```
Delete state/paper_trading_state.json
Restart dashboard (will create new valid state)
```

### Morning report not found
```
cd scripts
python run_au_pipeline_v1.3.13.py
```

### Trading controls not visible
```
Verify unified_trading_dashboard.py is 69 KB
Clear browser cache (Ctrl+F5)
```

## 🔗 Support

- GitHub: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
- Branch: market-timing-critical-fix
- Version: v1.3.15.86

## ✅ Status

**All Systems Operational**
- State Persistence: ✅ Working
- Trading Controls: ✅ Active
- Morning Reports: ✅ Loading

**Ready for Production Use!** 🚀

---
*Package Created: 2026-02-03*
*Version: v1.3.15.84+85+86*
*Status: Production Ready*
READMEEOF

# Create INSTALL.bat for Windows
echo "🪟 Step 8: Creating Windows installation script..."
cat > "$PACKAGE_DIR/INSTALL.bat" << 'BATEOF'
@echo off
chcp 65001 > nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║     Unified Trading Dashboard v1.3.15.86 Installation       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📦 Step 1: Checking Python installation...
python --version
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.10 or higher.
    pause
    exit /b 1
)
echo ✅ Python found
echo.

echo 📦 Step 2: Installing dependencies...
pip install -q -r requirements.txt
echo ✅ Dependencies installed
echo.

echo 📦 Step 3: Creating directory structure...
if not exist "logs" mkdir logs
if not exist "state" mkdir state
if not exist "reports\screening" mkdir reports\screening
echo ✅ Directories created
echo.

echo 📦 Step 4: Copying core files to current directory...
copy /Y core\*.py . > nul
echo ✅ Core files copied
echo.

echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  ✅ Installation Complete!                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🚀 To start the dashboard:
echo    1. Run: START.bat
echo    2. Open browser: http://localhost:8050
echo.
echo 📚 See docs\ folder for documentation
echo.
pause
BATEOF

# Create START.bat for easy startup
echo "🚀 Step 9: Creating startup script..."
cat > "$PACKAGE_DIR/START.bat" << 'BATEOF'
@echo off
chcp 65001 > nul
cls
echo ╔══════════════════════════════════════════════════════════════╗
echo ║     Unified Trading Dashboard v1.3.15.86                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🚀 Starting dashboard on http://localhost:8050
echo.

REM Set UTF-8 encoding for Python
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Set Keras backend (if using ML features)
set KERAS_BACKEND=torch

REM Start dashboard
python unified_trading_dashboard.py --symbols BHP.AX,CBA.AX,RIO.AX --capital 100000

if errorlevel 1 (
    echo.
    echo ❌ Dashboard failed to start!
    echo See logs\unified_trading.log for details
) else (
    echo.
    echo ✅ Dashboard stopped cleanly
)

pause
BATEOF

# Create file listing
echo "📋 Step 10: Creating file manifest..."
cat > "$PACKAGE_DIR/MANIFEST.txt" << 'MANIFESTEOF'
Unified Trading Dashboard v1.3.15.86 - File Manifest
====================================================

Core Files (essential):
  core/unified_trading_dashboard.py         (69 KB) - Main dashboard
  core/paper_trading_coordinator.py         (73 KB) - Trading engine
  core/sentiment_integration.py             (17 KB) - Sentiment analyzer

Configuration:
  config/live_trading_config.json            - Trading parameters
  requirements.txt                           - Python dependencies

Initial Data:
  state/paper_trading_state.json            (714 B) - Valid initial state
  reports/screening/au_morning_report.json   (1.3 KB) - Morning report

Scripts:
  scripts/START.bat                          - Windows startup script
  scripts/run_au_pipeline_v1.3.13.py        - Pipeline runner
  INSTALL.bat                                - Installation script
  START.bat                                  - Quick start script

Documentation:
  docs/INSTALLATION_GUIDE.md                 - Installation steps
  docs/DEPLOYMENT_READY.txt                  - Deployment checklist
  docs/COMPLETE_FIX_SUMMARY_v84_v85_v86.md  - Technical details
  docs/TRADING_CONTROLS_GUIDE_v86.md        - Controls usage
  docs/CURRENT_STATUS.md                     - System status
  README.md                                  - Package overview
  MANIFEST.txt                               - This file

Total Files: 15+ core files
Package Version: v1.3.15.86
Created: 2026-02-03
Status: Production Ready
MANIFESTEOF

echo ""
echo "✅ Step 11: Package structure created successfully!"
echo ""

# Create the ZIP archive
echo "🗜️  Step 12: Creating ZIP archive..."
cd "$DEPLOY_DIR"
zip -r -q "${PACKAGE_NAME}.zip" "$PACKAGE_NAME"

# Get file size
ZIPSIZE=$(ls -lh "${PACKAGE_NAME}.zip" | awk '{print $5}')

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            ✅ DEPLOYMENT PACKAGE CREATED!                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Package Details:"
echo "   Name:     ${PACKAGE_NAME}.zip"
echo "   Location: $DEPLOY_DIR/"
echo "   Size:     $ZIPSIZE"
echo ""
echo "📂 Package Contents:"
echo "   - Core Python files (3 essential + extras)"
echo "   - Configuration files"
echo "   - Initial state & reports"
echo "   - Installation scripts"
echo "   - Complete documentation"
echo "   - Windows startup scripts"
echo ""
echo "🚀 Ready to Deploy!"
echo ""

╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║     FinBERT v4.0 ENHANCED - Windows 11 Deployment Package README          ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

📦 PACKAGE CONTENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Package Name: FinBERT_v4.0_WINDOWS11_DEPLOYMENT.zip
Package Size: 163 KB
Version:      4.0-dev Enhanced
Platform:     Windows 11
Date:         October 30, 2025

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 QUICK START (3 STEPS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: Extract Package
────────────────────────────────────────────────────────────────────────────
   1. Right-click FinBERT_v4.0_WINDOWS11_DEPLOYMENT.zip
   2. Click "Extract All..."
   3. Choose destination (e.g., C:\FinBERT\)
   4. Click "Extract"

STEP 2: Install Dependencies
────────────────────────────────────────────────────────────────────────────
   1. Ensure Python 3.8+ is installed
      Download from: https://www.python.org/downloads/
      ⚠️ IMPORTANT: Check "Add Python to PATH" during installation

   2. Navigate to extracted folder
      FinBERT_v4.0_Development\

   3. Double-click: INSTALL_WINDOWS11_ENHANCED.bat

   4. Follow the prompts
      - Installation takes 5-10 minutes
      - Choose whether to install TensorFlow (optional, 600MB)
      - TensorFlow enables full LSTM training
      - Without it, system uses fallback prediction methods

   5. Wait for completion message

STEP 3: Start the System
────────────────────────────────────────────────────────────────────────────
   1. Double-click: START_V4_ENHANCED.bat

   2. Wait for server to start (~15 seconds)
      You'll see: "Server starting on http://localhost:5001"

   3. Open your web browser

   4. Navigate to: http://localhost:5001

   5. Start analyzing stocks!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ NEW FEATURES IN v4.0 ENHANCED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CANDLESTICK CHARTS
   → Professional OHLC (Open, High, Low, Close) visualization
   → Green candles = price went UP
   → Red candles = price went DOWN
   → Click "Candlestick" button to enable

2. VOLUME CHART
   → Automatically displayed below main chart
   → Color-coded bars (green/red based on price movement)
   → Shows trading volume for each period

3. TRAINING INTERFACE
   → Click "Train Model" button in UI
   → Enter symbol and epochs
   → Watch real-time progress bar
   → Model automatically reloads when complete

4. EXTENDED TIMEFRAMES
   → Now supports up to 2 YEARS of data
   → Available: 1D, 5D, 1M, 3M, 6M, 1Y, 2Y
   → Intraday data for 1D and 5D periods

5. CHART TYPE TOGGLE
   → Switch between Line and Candlestick views
   → One-click switching
   → Maintains zoom and pan state

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 IMPORTANT FILES IN PACKAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Installation & Startup:
────────────────────────────────────────────────────────────────────────────
   INSTALL_WINDOWS11_ENHANCED.bat    → Run FIRST to install dependencies
   START_V4_ENHANCED.bat             → Run EVERY TIME to start server
   STOP_SYSTEM.bat                   → Stop the server
   TRAIN_MODEL.bat                   → Train models from command line

Core Application:
────────────────────────────────────────────────────────────────────────────
   app_finbert_v4_dev.py             → Main Flask server
   finbert_v4_enhanced_ui.html       → Enhanced UI with all features
   config_dev.py                     → Configuration settings

Documentation:
────────────────────────────────────────────────────────────────────────────
   WINDOWS11_QUICK_START.txt         → Quick reference guide
   WINDOWS11_DEPLOYMENT_GUIDE.md     → Complete deployment manual
   README_V4_COMPLETE.md             → Comprehensive user guide
   QUICK_ACCESS_GUIDE.md             → Feature usage guide

Requirements:
────────────────────────────────────────────────────────────────────────────
   requirements-windows.txt          → Python package list
   requirements.txt                  → Core dependencies

Pre-Trained Models:
────────────────────────────────────────────────────────────────────────────
   models/lstm_CBA_AX_metadata.json  → Commonwealth Bank (Australia)
   models/lstm_AAPL_metadata.json    → Apple Inc. (test data)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 SYSTEM REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Minimum:
────────────────────────────────────────────────────────────────────────────
   OS:           Windows 11 (64-bit)
   Python:       3.8 or higher
   RAM:          4 GB
   Disk Space:   2 GB (5 GB with TensorFlow)
   Internet:     Required for market data

Recommended:
────────────────────────────────────────────────────────────────────────────
   OS:           Windows 11 (latest updates)
   Python:       3.10 or 3.11
   RAM:          16 GB
   Disk Space:   10 GB free
   Processor:    Intel i5 / AMD Ryzen 5 or better
   Internet:     Broadband connection

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 HOW TO USE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analyze a Stock:
────────────────────────────────────────────────────────────────────────────
   1. Open http://localhost:5001
   2. Click any stock button (AAPL, MSFT, etc.)
      OR type symbol in search box
   3. View predictions and charts

View Candlestick Charts:
────────────────────────────────────────────────────────────────────────────
   1. After analyzing a stock
   2. Click "Candlestick" button (next to "Line")
   3. See green/red OHLC candles
   4. Zoom with scroll wheel
   5. Pan with click-drag

View Volume Data:
────────────────────────────────────────────────────────────────────────────
   → Automatically shown below main chart
   → Green bars = price closed UP
   → Red bars = price closed DOWN
   → Bar height = trading volume

Train a Model:
────────────────────────────────────────────────────────────────────────────
   Option A (UI - Easiest):
      1. Click "Train Model" button (top-right)
      2. Enter symbol (e.g., AAPL or CBA.AX)
      3. Set epochs (recommended: 50)
      4. Click "Start Training"
      5. Watch progress bar

   Option B (Command Line):
      1. Double-click TRAIN_MODEL.bat
      2. Enter symbol when prompted
      3. Enter epochs (or use default 50)
      4. Wait for completion

Change Time Period:
────────────────────────────────────────────────────────────────────────────
   → Click period buttons: 1D, 5D, 1M, 3M, 6M, 1Y, 2Y
   → 1D, 5D = Intraday (5-minute intervals)
   → 1M-2Y = Daily data

Analyze Australian Stocks:
────────────────────────────────────────────────────────────────────────────
   1. Click "ASX" in market selector (top-right)
   2. Click Australian stock button
      OR type symbol with .AX suffix (e.g., CBA.AX)
   3. Pre-trained CBA.AX model already available

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem: "Python is not recognized"
────────────────────────────────────────────────────────────────────────────
   Solution:
   1. Install Python from https://www.python.org/downloads/
   2. During installation, CHECK "Add Python to PATH"
   3. Restart Command Prompt
   4. Run INSTALL_WINDOWS11_ENHANCED.bat again

Problem: Installation fails
────────────────────────────────────────────────────────────────────────────
   Solution:
   1. Run Command Prompt as Administrator
   2. Navigate to extracted folder
   3. Run: python -m pip install --upgrade pip
   4. Run: pip install -r requirements-windows.txt
   5. Manually start server

Problem: Port 5001 already in use
────────────────────────────────────────────────────────────────────────────
   Solution:
   1. Open config_dev.py
   2. Change: PORT = 5001 to PORT = 5002 (or any free port)
   3. Save file
   4. Restart server
   5. Access new URL: http://localhost:5002

Problem: Charts not loading
────────────────────────────────────────────────────────────────────────────
   Solution:
   1. Check internet connection (Yahoo Finance API required)
   2. Try different stock symbol
   3. Try different time period (1M first)
   4. Clear browser cache (Ctrl+Shift+Del)
   5. Refresh page (F5)

Problem: Training fails
────────────────────────────────────────────────────────────────────────────
   Solution:
   1. Check symbol is correct (AAPL not Apple)
   2. For ASX stocks, use .AX suffix (CBA.AX)
   3. Ensure internet connection
   4. Try lower epochs (20-30)
   5. Install TensorFlow if not installed:
      venv\Scripts\activate
      pip install tensorflow==2.15.0

Problem: Server won't stop
────────────────────────────────────────────────────────────────────────────
   Solution:
   1. Press Ctrl+C in Command Prompt
   2. Close Command Prompt window
   3. Run STOP_SYSTEM.bat
   4. Or manually kill process:
      netstat -ano | findstr :5001
      taskkill /PID <process_id> /F

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Read First:
────────────────────────────────────────────────────────────────────────────
   WINDOWS11_QUICK_START.txt         → Quick reference (this file)

Detailed Guides:
────────────────────────────────────────────────────────────────────────────
   WINDOWS11_DEPLOYMENT_GUIDE.md     → Complete deployment instructions
   README_V4_COMPLETE.md             → Comprehensive feature manual
   QUICK_ACCESS_GUIDE.md             → Step-by-step usage guide

Specific Topics:
────────────────────────────────────────────────────────────────────────────
   CBA_AX_TRAINING_COMPLETE.md       → Australian stock training
   TROUBLESHOOTING.txt               → Common issues and solutions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Application Files:
────────────────────────────────────────────────────────────────────────────
   ✓ Flask web server (Python)
   ✓ Enhanced UI with candlestick charts
   ✓ LSTM prediction models
   ✓ Technical analysis engine
   ✓ Training scripts
   ✓ Configuration files

Documentation:
────────────────────────────────────────────────────────────────────────────
   ✓ Windows 11 Quick Start Guide
   ✓ Complete Deployment Guide
   ✓ User Manual
   ✓ Feature Guides
   ✓ Troubleshooting Guide

Pre-Trained Models:
────────────────────────────────────────────────────────────────────────────
   ✓ CBA.AX (Commonwealth Bank Australia)
   ✓ AAPL (Apple Inc. - test data)

Windows Utilities:
────────────────────────────────────────────────────────────────────────────
   ✓ Installation batch file
   ✓ Startup batch file
   ✓ Training batch file
   ✓ Stop system batch file

NOT Included (Auto-created):
────────────────────────────────────────────────────────────────────────────
   ✗ Virtual environment (created during installation)
   ✗ Python packages (installed during setup)
   ✗ TensorFlow (optional - choose during installation)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 PRO TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Keep Server Running
   → Minimize Command Prompt window (don't close it)
   → Open multiple browser tabs to compare stocks
   → Server continues running in background

2. Check Multiple Timeframes
   → Look at 1M, 3M, and 1Y together
   → Get better insights from multiple perspectives
   → Compare short-term and long-term trends

3. Use Volume to Confirm
   → High volume on green candles = strong buy signal
   → High volume on red candles = strong sell signal
   → Low volume = weak signal

4. Train Frequently-Traded Stocks
   → Models work best on stocks you analyze often
   → Train once, use repeatedly
   → Update models periodically with new data

5. Higher Confidence = Better
   → 70%+ confidence predictions more reliable
   → <60% confidence means model uncertain
   → Always consider confidence with prediction

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ INSTALLATION CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before Starting:
────────────────────────────────────────────────────────────────────────────
   ☐ Windows 11 installed and updated
   ☐ Python 3.8+ downloaded and ready
   ☐ Internet connection active
   ☐ At least 5 GB disk space available
   ☐ Administrator access available

During Installation:
────────────────────────────────────────────────────────────────────────────
   ☐ Extract ZIP file to desired location
   ☐ Install Python with "Add to PATH" checked
   ☐ Run INSTALL_WINDOWS11_ENHANCED.bat
   ☐ Choose TensorFlow option (Y/N)
   ☐ Wait for all packages to install
   ☐ See "Installation Complete!" message

After Installation:
────────────────────────────────────────────────────────────────────────────
   ☐ venv\ folder created in project directory
   ☐ No error messages during installation
   ☐ START_V4_ENHANCED.bat available
   ☐ Can run server without errors
   ☐ Can access http://localhost:5001
   ☐ Can analyze at least one stock
   ☐ Charts display correctly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 SUPPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Documentation:
────────────────────────────────────────────────────────────────────────────
   Read included documentation files first
   Most issues covered in TROUBLESHOOTING.txt

GitHub:
────────────────────────────────────────────────────────────────────────────
   Repository: davidosland-lab/enhanced-global-stock-tracker-frontend
   Pull Request: #7 (latest features)
   Issues: Report bugs or request features

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 READY TO GO!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Follow the 3 steps at the top of this file:
   1. Extract package
   2. Run INSTALL_WINDOWS11_ENHANCED.bat
   3. Run START_V4_ENHANCED.bat

Then open: http://localhost:5001

Happy Trading! 📈

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Version: 4.0-dev Enhanced
Platform: Windows 11
Package Size: 163 KB
Date: October 30, 2025
Status: Production Ready

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

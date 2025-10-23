================================================================================
GSMT ENHANCED STOCK TRACKER - WINDOWS 11 COMPLETE INSTALLATION PACKAGE
Version 3.0 - ML Enhanced Edition with Phase 3 & 4 Models
================================================================================

QUICK START GUIDE
-----------------
1. Double-click "INSTALL.bat" to run the automated installer
2. Follow the on-screen prompts
3. The installer will create desktop shortcuts automatically

WHAT THIS PACKAGE INCLUDES
---------------------------
• Advanced ML Models:
  - LSTM & GRU Neural Networks for time-series prediction
  - Graph Neural Networks (GNN) for market relationship analysis
  - Transformer models for pattern recognition
  - CNN-LSTM hybrid architectures
  - Ensemble methods (Random Forest, XGBoost, LightGBM)
  - Reinforcement Learning with Q-Learning for trading signals

• Complete Technical Analysis:
  - RSI, MACD, Bollinger Bands
  - Moving Averages (5, 20, 50, 200-day)
  - ATR, Support/Resistance levels
  - Volume Profile analysis
  - Market regime detection

• Fixed Issues:
  ✓ Single stock tracker button now fully responsive
  ✓ Unified prediction API errors resolved
  ✓ Performance dashboard fully functional
  ✓ All Phase 3 & 4 models properly integrated

SYSTEM REQUIREMENTS
-------------------
• Windows 11 or Windows 10 (64-bit)
• Python 3.8 or higher (installer will check)
• 4GB RAM minimum (8GB recommended)
• 500MB free disk space
• Internet connection for real-time market data

INSTALLATION STEPS
------------------
1. Extract this folder to your desired location (e.g., C:\GSMT)
2. Right-click "INSTALL.bat" and select "Run as administrator" (recommended)
3. The installer will:
   - Check Python installation
   - Create a virtual environment
   - Install all required packages
   - Create desktop shortcuts
   - Configure the application
4. Choose "Y" when prompted to start the application

FOLDER STRUCTURE
----------------
GSMT_Windows11_Complete/
│
├── INSTALL.bat           # Main installer (run this first)
├── START_SERVER.bat      # Start the backend server
├── OPEN_DASHBOARD.bat    # Open web interface
├── STOP_SERVER.bat       # Stop the server
├── README.txt           # This file
│
├── backend/             # Backend server files
│   └── enhanced_ml_backend.py    # ML prediction engine
│
├── frontend/            # Web interface files
│   ├── dashboard.html   # Main integrated dashboard
│   └── tracker.html     # Single stock tracker
│
├── config/              # Configuration files
├── data/                # Data storage
├── logs/                # Application logs
└── venv/                # Virtual environment (created by installer)

HOW TO USE
----------
After installation, you have several options:

1. EASIEST METHOD:
   - Use the desktop shortcut "GSMT Stock Tracker"
   - Or double-click START_SERVER.bat, then OPEN_DASHBOARD.bat

2. MANUAL METHOD:
   - Open Command Prompt in this folder
   - Run: venv\Scripts\activate.bat
   - Run: python backend\enhanced_ml_backend.py
   - Open browser: http://localhost:8000

3. FEATURES AVAILABLE:
   • Real-time Stock Tracking
     - Enter any stock symbol (AAPL, MSFT, GOOGL, etc.)
     - Adjustable update intervals (5s to 1 min)
     - Live price charts with technical indicators

   • ML Predictions (All Models)
     - Click "Generate Prediction" for comprehensive analysis
     - View predictions from LSTM, GNN, Ensemble models
     - Get RL-based trading signals (BUY/SELL/HOLD)
     - Confidence scores for each model

   • Performance Dashboard
     - Monitor model accuracy in real-time
     - Compare performance across different models
     - View historical prediction accuracy

   • Strategy Backtesting
     - Test strategies over 1-6 month periods
     - Analyze returns, win rate, Sharpe ratio
     - Compare different model strategies

API ENDPOINTS
-------------
The backend provides REST API at http://localhost:8000

• GET /                                    # Dashboard interface
• GET /tracker                            # Stock tracker interface
• GET /health                             # Health check
• GET /docs                               # Interactive API documentation
• GET /api/unified-prediction/{symbol}    # Get ML predictions
• GET /api/backtest                       # Run strategy backtest
• GET /api/performance                    # Get model performance

Example API call:
http://localhost:8000/api/unified-prediction/AAPL?timeframe=5d

TROUBLESHOOTING
---------------
1. "Python not found" error:
   - Install Python from https://python.org
   - Make sure to check "Add Python to PATH" during installation
   - Restart your computer after Python installation

2. Port 8000 already in use:
   - Run STOP_SERVER.bat to stop any existing instance
   - Or edit backend/enhanced_ml_backend.py and change port number

3. Package installation fails:
   - Check internet connection
   - Try running as administrator
   - Manually install: pip install fastapi uvicorn yfinance pandas numpy scikit-learn

4. Browser doesn't open:
   - Manually navigate to http://localhost:8000
   - Try a different browser (Chrome, Firefox, Edge)

5. No data displayed:
   - Verify internet connection
   - Check if stock symbol is valid (try AAPL or MSFT)
   - Look at logs/ folder for error messages

UPDATING
--------
To update to a newer version:
1. Run STOP_SERVER.bat to stop the current server
2. Backup your data/ folder if needed
3. Extract new version over existing installation
4. Run INSTALL.bat again to update dependencies

UNINSTALL
---------
1. Run STOP_SERVER.bat
2. Delete this entire folder
3. Remove desktop shortcuts if created

TECHNICAL DETAILS
-----------------
• Backend: FastAPI + Uvicorn ASGI server
• ML Models: Custom implementations with scikit-learn base
• Data Source: Yahoo Finance API (yfinance)
• Frontend: HTML5 + JavaScript + TailwindCSS + Chart.js
• Python Version: 3.8+ required
• Dependencies: See requirements.txt for full list

SUPPORT
-------
• GitHub: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
• Issues: Report on GitHub Issues page
• API Docs: http://localhost:8000/docs (when server running)

VERSION HISTORY
---------------
v3.0 (Current) - Phase 3 & 4 ML Models Integration
  - Added LSTM, GNN, Transformer models
  - Implemented Reinforcement Learning
  - Fixed all known issues
  - Enhanced performance monitoring

v2.0 - Basic ML Integration
  - Added ensemble methods
  - Basic neural networks

v1.0 - Initial Release
  - Basic stock tracking
  - Simple predictions

LICENSE
-------
MIT License - See LICENSE file for details

================================================================================
Thank you for using GSMT Enhanced Stock Tracker!
================================================================================
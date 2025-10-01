#!/usr/bin/env python3
"""
Create a cloud-configured package for Stock Predictor Pro
"""

import zipfile
from pathlib import Path
from datetime import datetime

def create_cloud_package():
    print("📦 Creating Cloud-Configured Stock Predictor Package")
    print("=" * 60)
    
    root_dir = Path(__file__).parent
    
    # Files to include
    files = [
        "stock_predictor_configured.py",  # Main cloud-connected app
        "stock_predictor_lite.py",        # Fallback lite version
        "config.json",                    # Configuration with API endpoint
        "SETUP_CLOUD_CONNECTION.bat",     # Setup script
        "test_simple.py",                 # Python tester
    ]
    
    # Create README
    readme = """
STOCK PREDICTOR PRO - CLOUD CONFIGURED VERSION
===============================================

This package is PRE-CONFIGURED to connect to your cloud API!

API Endpoint: https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev

QUICK START:
------------
1. Extract all files to a folder (e.g., C:\StockPredictor)
2. Double-click: SETUP_CLOUD_CONNECTION.bat
3. The app will start and connect to your cloud API

FEATURES:
---------
✅ Pre-configured with your cloud API endpoint
✅ Real predictions from your ML models
✅ Cloud-based backtesting with historical data
✅ Local simulation mode as fallback
✅ Multiple ML models (ensemble, LSTM, XGBoost)
✅ Technical indicators from cloud

ABOUT BACKTESTING:
------------------
The application supports TWO types of backtesting:

1. CLOUD BACKTESTING (when connected):
   - Uses real historical data
   - Runs actual trading strategies
   - Provides accurate performance metrics
   - Calculates Sharpe ratio, drawdown, etc.
   - Available at: /api/backtest endpoint

2. LOCAL SIMULATION (offline mode):
   - Generates simulated results
   - Good for testing the interface
   - Not based on real data
   - Shows example metrics only

To use REAL backtesting:
- Make sure you're connected to cloud
- Go to Backtesting tab
- Select "Cloud" mode
- Enter parameters and run

TABS IN THE APPLICATION:
------------------------
1. PREDICTIONS: Get stock predictions
   - Enter symbol (AAPL, GOOGL, etc.)
   - Choose timeframe and model
   - Select Cloud API or Local Sim

2. BACKTESTING: Test strategies
   - Enter date range
   - Choose strategy type
   - Set initial capital
   - Run with Cloud or Local

3. SETTINGS: Configure API
   - Update cloud endpoint if needed
   - Test connection
   - Save configuration

4. STATUS: System information
   - Shows connection status
   - Lists available features

TROUBLESHOOTING:
----------------
If cloud connection fails:
- Check internet connection
- Verify API endpoint is correct
- Try "Test Connection" in Settings
- App will fall back to local simulation

The config.json file contains your API endpoint.
You can edit it if the endpoint changes.

REQUIREMENTS:
-------------
- Python 3.9 or higher
- requests library (for cloud features)
  Install with: pip install requests

© 2024 Stock Predictor Team
"""
    
    # Create package
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    zip_name = f"StockPredictorPro_CLOUD_CONFIGURED_{timestamp}.zip"
    zip_path = root_dir / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add README
        zipf.writestr("README_CLOUD_VERSION.txt", readme)
        
        # Add all files
        for filename in files:
            file_path = root_dir / filename
            if file_path.exists():
                zipf.write(file_path, filename)
                print(f"  ✓ Added {filename}")
    
    size_kb = zip_path.stat().st_size / 1024
    
    print("\n" + "=" * 60)
    print("✅ Cloud-Configured Package Created!")
    print(f"📦 File: {zip_name}")
    print(f"💾 Size: {size_kb:.1f} KB")
    print("\n🌐 This package includes:")
    print("  • Your cloud API endpoint pre-configured")
    print("  • Full backtesting capabilities")
    print("  • Real predictions from cloud")
    print("  • Fallback local simulation")
    print("=" * 60)
    
    return zip_path

if __name__ == "__main__":
    create_cloud_package()
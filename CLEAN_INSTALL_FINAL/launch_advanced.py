#!/usr/bin/env python3
"""
Enhanced Windows 11 Stock Tracker Launcher
With all advanced features enabled
"""
import os
import sys
import subprocess
import time

def main():
    print("=" * 60)
    print("WINDOWS 11 STOCK TRACKER - ADVANCED EDITION")
    print("=" * 60)
    print("Features:")
    print("  ✅ CBA Enhanced with Documents & Media Analysis")
    print("  ✅ Phase 4 Predictor with Detailed Backtesting")
    print("  ✅ Local Storage (100x faster backtesting)")
    print("  ✅ Document Uploader with FinBERT")
    print("  ✅ Real Yahoo Finance Data")
    print("=" * 60)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n📦 Installing requirements...")
    requirements = [
        "yfinance", "fastapi", "uvicorn", "pandas", "numpy",
        "cachetools", "pytz", "python-multipart", "aiofiles",
        "websockets", "python-dotenv", "sqlite3"
    ]
    
    subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + requirements)
    
    # Initialize database if needed
    if os.path.exists("historical_data_manager.py"):
        print("\n💾 Initializing local storage...")
        subprocess.run([sys.executable, "-c", "from historical_data_manager import HistoricalDataManager; hdm = HistoricalDataManager(); print('Local storage ready')"])
    
    print("\n🚀 Starting backend on http://localhost:8002")
    print("\n📊 Available Modules:")
    print("  1. CBA Enhanced Tracker - http://localhost:8002/modules/cba_enhanced.html")
    print("  2. Global Indices - http://localhost:8002/modules/global_market_tracker.html")
    print("  3. Stock Tracker - http://localhost:8002/modules/stock_tracker.html")
    print("  4. Document Analyzer - http://localhost:8002/modules/document_uploader.html")
    print("  5. Phase 4 Predictor - http://localhost:8002/modules/prediction_centre_phase4.html")
    print("\nMain Interface: http://localhost:8002")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the backend
    subprocess.run([sys.executable, "backend.py"])

if __name__ == "__main__":
    main()

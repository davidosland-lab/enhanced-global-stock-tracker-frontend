#!/usr/bin/env python3
import os
import sys
import subprocess
import time

def main():
    print("=" * 50)
    print("Windows 11 Stock Tracker Launcher")
    print("=" * 50)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n📦 Installing requirements...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", 
                   "yfinance", "fastapi", "uvicorn", "pandas", "numpy", 
                   "cachetools", "pytz", "python-multipart"])
    
    print("\n🚀 Starting backend on http://localhost:8002")
    print("Access the application at: http://localhost:8002")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the backend
    subprocess.run([sys.executable, "backend.py"])

if __name__ == "__main__":
    main()

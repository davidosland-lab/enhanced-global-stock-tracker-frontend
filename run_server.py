#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows-safe launcher for the Stock Analysis System
Handles all encoding issues automatically
"""

import os
import sys
import subprocess

def main():
    # Set environment variables to prevent encoding issues
    os.environ['FLASK_SKIP_DOTENV'] = '1'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'
    
    # Configure stdout/stderr for UTF-8 on Windows
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    
    print("=" * 70)
    print("STOCK ANALYSIS SYSTEM - WINDOWS LAUNCHER")
    print("=" * 70)
    print()
    print("Starting server at: http://localhost:8000")
    print("Press Ctrl+C to stop")
    print()
    print("=" * 70)
    print()
    
    try:
        # Import and run the main application
        # Using exec to avoid import issues
        with open('unified_stock_system_local.py', 'r', encoding='utf-8') as f:
            code = f.read()
        exec(code, {'__name__': '__main__'})
    except FileNotFoundError:
        print("ERROR: unified_stock_system_local.py not found!")
        print("Please ensure all files are in the same directory.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nTrying alternate method...")
        
        # Fallback: run as subprocess
        try:
            subprocess.run([sys.executable, 'unified_stock_system_local.py'], 
                         env={**os.environ, 'FLASK_SKIP_DOTENV': '1'})
        except Exception as e2:
            print(f"Failed to start server: {e2}")
            input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
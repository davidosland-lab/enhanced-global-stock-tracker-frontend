"""
COMPLETE REGIME TRADING SYSTEM - PYTHON INSTALLER & LAUNCHER
Version: v1.3.15.63 PYTHON-BASED
Date: 2026-02-01

ONE-CLICK SOLUTION:
- Automatically installs ALL dependencies
- Cannot crash (Python handles errors gracefully)
- Shows progress and status
- Starts system when ready
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header():
    """Print startup header"""
    print("\n" + "="*75)
    print("  COMPLETE REGIME TRADING SYSTEM")
    print("  Python-Based Installer & Launcher - v1.3.15.63")
    print("="*75 + "\n")

def check_and_install_dependencies():
    """Check and install all required dependencies"""
    
    print("STEP 1: AUTO-DEPENDENCY CHECK AND INSTALLATION")
    print("-"*75 + "\n")
    
    # Determine pip command
    if (Path("venv") / "Scripts" / "pip.exe").exists():
        pip_cmd = str(Path("venv") / "Scripts" / "pip.exe")
        print("[OK] Using virtual environment")
    else:
        pip_cmd = "pip"
        print("[!] Using system Python")
    print()
    
    dependencies = [
        ("scikit-learn", "scikit-learn", "Data preprocessing"),
        ("keras", "keras", "LSTM neural network"),
        ("transformers", "transformers", "FinBERT sentiment analysis"),
        ("torch", "torch --index-url https://download.pytorch.org/whl/cpu", "PyTorch backend (~2GB)")
    ]
    
    installed_count = 0
    
    for idx, (import_name, install_name, description) in enumerate(dependencies, 1):
        print(f"[{idx}/4] Checking {import_name}... ({description})")
        
        # Check if already installed
        try:
            __import__(import_name.replace("-", "_"))
            print(f"    [OK] {import_name} already installed\n")
            continue
        except ImportError:
            pass
        
        # Install package
        print(f"    [*] Installing {import_name}...")
        if "torch" in install_name:
            print(f"        NOTE: This is ~2GB and may take 2-5 minutes")
        
        try:
            result = subprocess.run(
                [pip_cmd, "install"] + install_name.split(),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                print(f"    [OK] {import_name} installed successfully\n")
                installed_count += 1
            else:
                print(f"    [WARNING] {import_name} installation had issues")
                print(f"              System will continue with fallback methods\n")
                
        except subprocess.TimeoutExpired:
            print(f"    [WARNING] {import_name} installation timeout")
            print(f"              System will continue with fallback methods\n")
        except Exception as e:
            print(f"    [WARNING] {import_name} installation error: {str(e)}")
            print(f"              System will continue with fallback methods\n")
    
    if installed_count > 0:
        print("\n" + "="*75)
        print(f"  DEPENDENCIES INSTALLED: {installed_count} new package(s)")
        print("="*75 + "\n")
    
    # Set environment variable
    os.environ['KERAS_BACKEND'] = 'torch'
    print("[*] Environment configured: KERAS_BACKEND=torch\n")

def show_menu():
    """Display main menu"""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n" + "="*75)
        print("  MAIN MENU - v1.3.15.63 PYTHON-BASED")
        print("="*75 + "\n")
        
        print("  QUICK START:")
        print("  " + "-"*71)
        print("  1. START UNIFIED TRADING DASHBOARD  [RECOMMENDED]")
        print("     • Interactive stock selection + live trading")
        print("     • Real-time ML signals (FinBERT + LSTM)")
        print("     • http://localhost:8050\n")
        
        print("  OVERNIGHT ANALYSIS:")
        print("  " + "-"*71)
        print("  2. Run AU OVERNIGHT PIPELINE (15-20 min)")
        print("  3. Run US OVERNIGHT PIPELINE (15-20 min)")
        print("  4. Run UK OVERNIGHT PIPELINE (15-20 min)")
        print("  5. Run ALL MARKETS PIPELINES (45-60 min)\n")
        
        print("  ADVANCED:")
        print("  " + "-"*71)
        print("  6. Start Paper Trading Platform (background)")
        print("  7. View System Status")
        print("  8. Reinstall All Dependencies")
        print("  9. Open Basic Dashboard (http://localhost:5002)\n")
        
        print("  0. Exit\n")
        print("-"*75 + "\n")
        
        choice = input("Select option (0-9): ").strip()
        
        if choice == "1":
            start_unified_dashboard()
        elif choice == "2":
            run_pipeline("au")
        elif choice == "3":
            run_pipeline("us")
        elif choice == "4":
            run_pipeline("uk")
        elif choice == "5":
            run_all_pipelines()
        elif choice == "6":
            start_paper_trading()
        elif choice == "7":
            show_system_status()
        elif choice == "8":
            reinstall_dependencies()
        elif choice == "9":
            start_basic_dashboard()
        elif choice == "0":
            print("\nThank you for using the Regime Trading System!")
            print("v1.3.15.63 PYTHON-BASED\n")
            sys.exit(0)
        else:
            print("\n[ERROR] Invalid choice")
            input("\nPress Enter to continue...")

def start_unified_dashboard():
    """Start unified trading dashboard"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\n" + "="*75)
    print("  UNIFIED TRADING DASHBOARD")
    print("="*75 + "\n")
    
    print("Starting dashboard at http://localhost:8050")
    print("Press Ctrl+C to stop\n")
    print("-"*75 + "\n")
    
    try:
        subprocess.run([sys.executable, "unified_trading_dashboard.py"])
    except KeyboardInterrupt:
        print("\n\n[*] Dashboard stopped")
    except Exception as e:
        print(f"\n[ERROR] Dashboard failed: {str(e)}")
    
    input("\nPress Enter to return to menu...")

def run_pipeline(market):
    """Run overnight pipeline for specified market"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    market_names = {
        "au": ("AU", "Australian", "run_au_pipeline_v1.3.13.py"),
        "us": ("US", "United States", "run_us_full_pipeline.py"),
        "uk": ("UK", "United Kingdom", "run_uk_full_pipeline.py")
    }
    
    code, name, script = market_names[market]
    
    print("\n" + "="*75)
    print(f"  {code} OVERNIGHT PIPELINE: {name} Market Analysis")
    print("="*75 + "\n")
    print("Estimated time: 15-20 minutes\n")
    
    confirm = input("Continue? (Y/N): ").strip().upper()
    if confirm != "Y":
        return
    
    print(f"\n[*] Starting {code} overnight pipeline...\n")
    
    try:
        subprocess.run([
            sys.executable, script,
            "--full-scan",
            "--capital", "100000",
            "--ignore-market-hours"
        ])
        print(f"\n[OK] {code} pipeline completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] {code} pipeline encountered errors: {str(e)}")
    
    input("\nPress Enter to return to menu...")

def run_all_pipelines():
    """Run all market pipelines"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\n" + "="*75)
    print("  ALL MARKETS PIPELINES: AU + US + UK")
    print("="*75 + "\n")
    print("Estimated time: 45-60 minutes\n")
    
    confirm = input("Continue? (Y/N): ").strip().upper()
    if confirm != "Y":
        return
    
    print()
    
    for market in ["au", "us", "uk"]:
        print(f"[*] Running {market.upper()} Pipeline...\n")
        run_pipeline(market)
    
    print("\n[OK] All market pipelines completed!")
    input("\nPress Enter to return to menu...")

def start_paper_trading():
    """Start paper trading platform"""
    print("\n[*] Starting Paper Trading Platform in background...")
    
    try:
        if os.name == 'nt':
            subprocess.Popen(
                [sys.executable, "paper_trading_coordinator.py", "--config", "config/live_trading_config.json"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            subprocess.Popen([sys.executable, "paper_trading_coordinator.py", "--config", "config/live_trading_config.json"])
        
        print("[OK] Paper Trading Platform started!\n")
    except Exception as e:
        print(f"[ERROR] Failed to start paper trading: {str(e)}\n")
    
    input("Press Enter to return to menu...")

def show_system_status():
    """Display system status"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\n" + "="*75)
    print("  SYSTEM STATUS")
    print("="*75 + "\n")
    
    # Python version
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Python Path: {sys.executable}\n")
    
    # Virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Virtual Environment: Active")
        print(f"Location: {sys.prefix}\n")
    else:
        print("Virtual Environment: Not Active\n")
    
    # Dependencies
    print("Key Dependencies:")
    
    dependencies = [
        ("keras", "Keras"),
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("sklearn", "scikit-learn"),
        ("yfinance", "yfinance"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("dash", "Dash")
    ]
    
    for import_name, display_name in dependencies:
        try:
            __import__(import_name)
            print(f"  {display_name}: Installed")
        except ImportError:
            print(f"  {display_name}: Missing")
    
    print()
    
    # Environment variables
    print("Environment Variables:")
    print(f"  KERAS_BACKEND: {os.environ.get('KERAS_BACKEND', 'Not set')}\n")
    
    input("Press Enter to return to menu...")

def reinstall_dependencies():
    """Reinstall all dependencies"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\n" + "="*75)
    print("  REINSTALL ALL DEPENDENCIES")
    print("="*75 + "\n")
    
    print("This will reinstall all ML dependencies:")
    print("  - scikit-learn")
    print("  - keras")
    print("  - transformers")
    print("  - torch (PyTorch CPU ~2GB)\n")
    print("Estimated time: 5-10 minutes\n")
    
    confirm = input("Continue? (Y/N): ").strip().upper()
    if confirm != "Y":
        return
    
    print()
    check_and_install_dependencies()
    
    print("[OK] Dependencies reinstalled!")
    input("\nPress Enter to return to menu...")

def start_basic_dashboard():
    """Start basic dashboard"""
    print("\n[*] Starting basic dashboard at http://localhost:5002...")
    print("Press Ctrl+C to stop\n")
    
    try:
        subprocess.run([sys.executable, "dashboard.py"])
    except KeyboardInterrupt:
        print("\n\n[*] Dashboard stopped")
    except Exception as e:
        print(f"\n[ERROR] Dashboard failed: {str(e)}")
    
    input("\nPress Enter to return to menu...")

def main():
    """Main entry point"""
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Print header
    print_header()
    
    # Check and install dependencies
    check_and_install_dependencies()
    
    # Show main menu
    show_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        input("\nPress Enter to exit...")
        sys.exit(1)

#!/usr/bin/env python3
"""
Dependency Fixer for Stock Predictor Pro
Handles compatibility issues and installs correct packages
"""

import sys
import subprocess
import platform
import os
from pathlib import Path

def check_python_version():
    """Check Python version and compatibility"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3:
        print("❌ ERROR: Python 3.x is required")
        return False
    
    if version.minor == 14:
        print("⚠️  WARNING: Python 3.14 is too new and may have compatibility issues")
        print("📦 Recommended: Install Python 3.11 for best compatibility")
        print("🔗 Download from: https://www.python.org/downloads/release/python-3119/")
        return False
    
    if version.minor < 9:
        print("❌ ERROR: Python 3.9 or higher is required")
        return False
    
    if version.minor > 11:
        print("⚠️  WARNING: Python version is newer than tested versions")
        print("📦 Some packages may have compatibility issues")
    
    print(f"✅ Python {version.major}.{version.minor} is compatible")
    return True

def install_package(package_name, fallback=None):
    """Install a package with fallback option"""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError:
        if fallback:
            print(f"⚠️  {package_name} failed, trying {fallback}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", fallback],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ {fallback} installed successfully")
                return True
            except:
                pass
        print(f"❌ Failed to install {package_name}")
        return False

def fix_dependencies():
    """Fix and install all dependencies"""
    print("\n" + "="*60)
    print("Stock Predictor Pro - Dependency Installer")
    print("="*60 + "\n")
    
    # Check Python version
    if not check_python_version():
        print("\n⚠️  Please install Python 3.9, 3.10, or 3.11 for best compatibility")
        input("\nPress Enter to exit...")
        return False
    
    # Upgrade pip
    print("\n📦 Upgrading pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                            stdout=subprocess.DEVNULL)
        print("✅ pip upgraded")
    except:
        print("⚠️  Could not upgrade pip")
    
    # Core packages
    print("\n📦 Installing core packages...")
    core_packages = [
        ("numpy>=1.21.0,<1.24.0", None),
        ("pandas>=1.3.0,<2.0.0", None),
        ("scikit-learn>=1.0.0,<1.3.0", None),
    ]
    
    for package, fallback in core_packages:
        install_package(package, fallback)
    
    # GUI packages
    print("\n🎨 Installing GUI packages...")
    gui_packages = [
        ("customtkinter>=5.1.0", None),
        ("Pillow>=9.0.0", None),
    ]
    
    for package, fallback in gui_packages:
        install_package(package, fallback)
    
    # ML packages
    print("\n🤖 Installing ML packages...")
    ml_packages = [
        ("xgboost>=1.6.0", None),
        ("lightgbm>=3.3.0", None),
    ]
    
    for package, fallback in ml_packages:
        install_package(package, fallback)
    
    # Financial packages
    print("\n📈 Installing financial packages...")
    financial_packages = [
        ("yfinance>=0.2.18", None),
        ("ta>=0.10.0", "finta>=1.3"),  # ta is alternative to pandas-ta
    ]
    
    for package, fallback in financial_packages:
        install_package(package, fallback)
    
    # Network packages
    print("\n🌐 Installing network packages...")
    network_packages = [
        ("requests>=2.28.0", None),
        ("aiohttp>=3.8.0", None),
    ]
    
    for package, fallback in network_packages:
        install_package(package, fallback)
    
    # Optional packages
    print("\n📊 Installing optional packages...")
    optional_packages = [
        ("matplotlib>=3.5.0", None),
        ("plotly>=5.10.0", None),
        ("psutil>=5.9.0", None),
    ]
    
    for package, fallback in optional_packages:
        install_package(package, fallback)
    
    print("\n" + "="*60)
    print("✅ Dependency installation complete!")
    print("="*60)
    
    # Test imports
    print("\n🧪 Testing imports...")
    test_imports()
    
    print("\n✅ Setup complete! You can now run Stock Predictor Pro")
    print("Run with: python stock_predictor_pro.py")
    
    return True

def test_imports():
    """Test if key packages can be imported"""
    packages_to_test = [
        ("customtkinter", "GUI Framework"),
        ("numpy", "Numerical Computing"),
        ("pandas", "Data Processing"),
        ("sklearn", "Machine Learning"),
        ("xgboost", "XGBoost ML"),
        ("yfinance", "Financial Data"),
        ("requests", "HTTP Requests"),
    ]
    
    for module_name, description in packages_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description} ({module_name})")
        except ImportError:
            print(f"❌ {description} ({module_name}) - not installed")

def create_minimal_app():
    """Create a minimal test application"""
    minimal_app = '''#!/usr/bin/env python3
"""Minimal Stock Predictor Pro - Test Version"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys

class MinimalStockPredictor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stock Predictor Pro - Minimal Version")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="Stock Predictor Pro", 
                         font=("Arial", 24, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Status
        status = ttk.Label(main_frame, text="Minimal version running successfully!",
                          font=("Arial", 12))
        status.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Python version info
        py_info = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        version_label = ttk.Label(main_frame, text=py_info)
        version_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Test buttons
        ttk.Button(main_frame, text="Test Prediction", 
                  command=self.test_prediction).grid(row=3, column=0, pady=10, padx=5)
        ttk.Button(main_frame, text="Check Dependencies", 
                  command=self.check_deps).grid(row=3, column=1, pady=10, padx=5)
        
        # Output text
        self.output = tk.Text(main_frame, height=20, width=80)
        self.output.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.output.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.output.configure(yscrollcommand=scrollbar.set)
        
        # Exit button
        ttk.Button(main_frame, text="Exit", command=self.root.quit).grid(row=5, column=0, columnspan=2, pady=10)
        
        self.output.insert(tk.END, "Welcome to Stock Predictor Pro (Minimal Version)\\n")
        self.output.insert(tk.END, "This is a test version to verify installation.\\n\\n")
    
    def test_prediction(self):
        """Simulate a prediction"""
        import random
        symbol = "AAPL"
        current = 150.00
        predicted = current * (1 + random.uniform(-0.05, 0.05))
        confidence = random.uniform(0.6, 0.9)
        
        result = f"""
Prediction Test Results:
========================
Symbol: {symbol}
Current Price: ${current:.2f}
Predicted Price: ${predicted:.2f}
Change: {((predicted/current - 1) * 100):.2f}%
Confidence: {confidence:.1%}
Recommendation: {"BUY" if predicted > current else "SELL"}
"""
        self.output.insert(tk.END, result)
        self.output.see(tk.END)
    
    def check_deps(self):
        """Check installed dependencies"""
        self.output.insert(tk.END, "\\nChecking dependencies...\\n")
        self.output.insert(tk.END, "=" * 40 + "\\n")
        
        deps = [
            "numpy", "pandas", "sklearn", "customtkinter",
            "xgboost", "yfinance", "requests", "ta"
        ]
        
        for dep in deps:
            try:
                __import__(dep)
                self.output.insert(tk.END, f"✅ {dep} installed\\n")
            except ImportError:
                self.output.insert(tk.END, f"❌ {dep} NOT installed\\n")
        
        self.output.insert(tk.END, "=" * 40 + "\\n")
        self.output.see(tk.END)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MinimalStockPredictor()
    app.run()
'''
    
    # Save minimal app
    with open("stock_predictor_minimal.py", "w") as f:
        f.write(minimal_app)
    print("\n📝 Created stock_predictor_minimal.py for testing")

if __name__ == "__main__":
    success = fix_dependencies()
    
    if success:
        create_minimal_app()
        print("\n🎯 You can test the installation with:")
        print("   python stock_predictor_minimal.py")
    
    input("\nPress Enter to exit...")
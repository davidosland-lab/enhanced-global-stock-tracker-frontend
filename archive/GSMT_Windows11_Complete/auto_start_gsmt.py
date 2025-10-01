#!/usr/bin/env python3
"""
GSMT Ver 8.1.3 - Automated Launcher with Landing Dashboard
Cross-platform launcher for Windows, Mac, and Linux
"""

import sys
import os
import subprocess
import time
import webbrowser
import platform
import socket
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print application header"""
    print(f"\n{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'GSMT STOCK TRACKER Ver 8.1.3':^80}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'Automated Launcher with Landing Dashboard':^80}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*80}{Colors.RESET}\n")

def check_port(port):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def kill_process_on_port(port):
    """Kill process running on specified port"""
    system = platform.system()
    
    try:
        if system == "Windows":
            # Find and kill process on Windows
            result = subprocess.run(
                f'netstat -aon | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'LISTENING' in line:
                        parts = line.split()
                        pid = parts[-1]
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                        print(f"  Killed process on port {port}")
                        return True
        else:
            # Unix-based systems (Mac, Linux)
            result = subprocess.run(
                f"lsof -ti:{port}",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                pid = result.stdout.strip()
                subprocess.run(f"kill -9 {pid}", shell=True)
                print(f"  Killed process on port {port}")
                return True
                
    except Exception as e:
        print(f"  Warning: Could not kill process on port {port}: {e}")
    
    return False

def install_dependencies():
    """Check and install required Python packages"""
    packages = {
        'fastapi': 'FastAPI framework',
        'uvicorn': 'ASGI server',
        'yfinance': 'Yahoo Finance API',
        'pandas': 'Data processing',
        'numpy': 'Numerical computing',
        'scikit-learn': 'Machine learning',
        'aiofiles': 'Async file operations'
    }
    
    print(f"{Colors.BOLD}[STEP 2] Checking required packages...{Colors.RESET}")
    
    for package, description in packages.items():
        try:
            __import__(package.replace('-', '_'))
            print(f"  {Colors.GREEN}✓{Colors.RESET} {description}")
        except ImportError:
            print(f"  Installing {description}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package, "--quiet"],
                check=False
            )
            print(f"  {Colors.GREEN}✓{Colors.RESET} {description} installed")
    
    print(f"{Colors.GREEN}[OK] All required packages installed{Colors.RESET}\n")

def start_server(name, script_path, port):
    """Start a backend server"""
    print(f"Starting {name} on port {port}...")
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    # Wait for server to start
    max_attempts = 10
    for i in range(max_attempts):
        time.sleep(1)
        if not check_port(port):  # Port is now in use
            print(f"  {Colors.GREEN}✓{Colors.RESET} {name} is running on http://localhost:{port}")
            return process
        
    print(f"  {Colors.YELLOW}⚠{Colors.RESET} {name} may be starting slowly")
    return process

def test_server(url, name):
    """Test if a server is responding"""
    try:
        import requests
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def create_desktop_shortcut():
    """Create desktop shortcut for the landing page"""
    system = platform.system()
    
    try:
        if system == "Windows":
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "GSMT Dashboard.url"
            
            landing_page = Path(__file__).parent / "frontend" / "landing_dashboard.html"
            
            with open(shortcut_path, 'w') as f:
                f.write("[InternetShortcut]\n")
                f.write(f"URL=file:///{landing_page.as_posix()}\n")
                f.write("IconIndex=0\n")
                f.write("IconFile=%SystemRoot%\\system32\\SHELL32.dll,13\n")
            
            print(f"  {Colors.GREEN}✓{Colors.RESET} Desktop shortcut created")
        else:
            print(f"  {Colors.YELLOW}ℹ{Colors.RESET} Desktop shortcuts not supported on {system}")
    except Exception as e:
        print(f"  {Colors.YELLOW}⚠{Colors.RESET} Could not create shortcut: {e}")

def main():
    """Main launcher function"""
    print_header()
    
    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    backend_dir = script_dir / "backend"
    frontend_dir = script_dir / "frontend"
    
    print(f"Starting complete GSMT system with real market data from Yahoo Finance...\n")
    
    # Step 1: Check Python version
    print(f"{Colors.BOLD}[STEP 1] Checking Python installation...{Colors.RESET}")
    python_version = sys.version.split()[0]
    print(f"  {Colors.GREEN}✓{Colors.RESET} Python {python_version} detected")
    
    if sys.version_info < (3, 7):
        print(f"{Colors.RED}ERROR: Python 3.7 or higher required!{Colors.RESET}")
        sys.exit(1)
    print()
    
    # Step 2: Install dependencies
    install_dependencies()
    
    # Step 3: Clear ports
    print(f"{Colors.BOLD}[STEP 3] Clearing ports 8000 and 8001...{Colors.RESET}")
    
    if not check_port(8000):
        kill_process_on_port(8000)
    if not check_port(8001):
        kill_process_on_port(8001)
    
    print(f"  {Colors.GREEN}✓{Colors.RESET} Ports cleared\n")
    
    # Step 4: Start Market Data Server
    print(f"{Colors.BOLD}[STEP 4] Starting Market Data Server (Real Yahoo Finance data)...{Colors.RESET}")
    market_server_path = backend_dir / "market_data_server.py"
    market_process = start_server("Market Data Server", str(market_server_path), 8000)
    print()
    
    # Step 5: Start CBA Specialist Server
    print(f"{Colors.BOLD}[STEP 5] Starting CBA Specialist Server (Real CBA.AX data)...{Colors.RESET}")
    cba_server_path = backend_dir / "cba_specialist_server.py"
    cba_process = start_server("CBA Specialist Server", str(cba_server_path), 8001)
    print()
    
    # Step 6: Create desktop shortcut
    print(f"{Colors.BOLD}[STEP 6] Creating desktop shortcut...{Colors.RESET}")
    create_desktop_shortcut()
    print()
    
    # Step 7: Wait for initialization
    print(f"{Colors.BOLD}[STEP 7] Waiting for servers to fully initialize...{Colors.RESET}")
    time.sleep(3)
    print(f"  {Colors.GREEN}✓{Colors.RESET} Servers ready\n")
    
    # Step 8: Open landing dashboard
    print(f"{Colors.BOLD}[STEP 8] Opening GSMT Landing Dashboard...{Colors.RESET}")
    landing_page = frontend_dir / "landing_dashboard.html"
    webbrowser.open(f"file:///{landing_page.as_posix()}")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Dashboard opened in browser\n")
    
    # Display success message
    print(f"\n{Colors.GREEN}{'='*80}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}{'✓ GSMT SUCCESSFULLY LAUNCHED!':^80}{Colors.RESET}")
    print(f"{Colors.GREEN}{'='*80}{Colors.RESET}\n")
    
    print(f"{Colors.CYAN}▶ SERVERS RUNNING:{Colors.RESET}")
    print(f"  • Market Data Server:     http://localhost:8000")
    print(f"  • CBA Specialist Server:  http://localhost:8001\n")
    
    print(f"{Colors.CYAN}▶ LANDING DASHBOARD OPENED:{Colors.RESET}")
    print(f"  • Shows all 6 modules with live data")
    print(f"  • Real-time market prices from Yahoo Finance")
    print(f"  • Click any module card to open detailed view\n")
    
    print(f"{Colors.CYAN}▶ AVAILABLE MODULES:{Colors.RESET}")
    print(f"  1. Global Market Indices  - 18 worldwide markets")
    print(f"  2. CBA Banking Analysis   - Commonwealth Bank specialist")
    print(f"  3. ML Predictions        - 6 AI models (LSTM, GRU, Transformer, etc.)")
    print(f"  4. Technical Analysis    - RSI, MACD, Bollinger, patterns")
    print(f"  5. Single Stock Tracker  - Track any stock with predictions")
    print(f"  6. Performance Dashboard - Model accuracy metrics\n")
    
    print(f"{Colors.CYAN}▶ DATA FEATURES:{Colors.RESET}")
    print(f"  • Real market data (no synthetic/fake data)")
    print(f"  • 5-minute cache for optimal performance")
    print(f"  • Live updates during market hours")
    print(f"  • Historical data for analysis\n")
    
    print(f"{Colors.YELLOW}To stop servers: Press Ctrl+C or close this window{Colors.RESET}")
    print(f"{Colors.YELLOW}To restart: Run auto_start_gsmt.py again{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}{'='*80}{Colors.RESET}\n")
    
    # Keep running
    try:
        print("Press Ctrl+C to stop all servers...\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Shutting down servers...{Colors.RESET}")
        try:
            market_process.terminate()
            cba_process.terminate()
        except:
            pass
        print(f"{Colors.GREEN}Servers stopped. Goodbye!{Colors.RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
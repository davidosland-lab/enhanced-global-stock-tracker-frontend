#!/usr/bin/env python3
"""
Simple Stock Tracker Startup Script
More reliable than batch files
"""

import subprocess
import sys
import os
import time
import webbrowser
import platform

def check_python():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"ERROR: Python 3.7+ required, you have {sys.version}")
        return False
    print(f"✓ Python {sys.version.split()[0]} detected")
    return True

def install_packages():
    """Install minimal required packages"""
    print("\nInstalling essential packages...")
    print("This may take 2-3 minutes on first run...\n")
    
    essential_packages = [
        'fastapi',
        'uvicorn',
        'yfinance',
        'pandas',
        'numpy',
        'pytz',
        'python-multipart',
        'httpx',
        'aiofiles'
    ]
    
    for i, package in enumerate(essential_packages, 1):
        print(f"[{i}/{len(essential_packages)}] Installing {package}...")
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', package, '--quiet'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"    ✓ {package} installed")
        except:
            print(f"    ⚠ {package} may already be installed")
    
    print("\n✓ Package installation complete!")

def kill_existing_processes():
    """Kill any existing Python processes on our ports"""
    print("\nCleaning up any existing services...")
    
    if platform.system() == 'Windows':
        # Windows
        ports = [8000, 8002, 8003]
        for port in ports:
            try:
                # Find process using port
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                for line in result.stdout.split('\n'):
                    if 'LISTENING' in line:
                        parts = line.split()
                        if parts:
                            pid = parts[-1]
                            subprocess.run(f'taskkill /F /PID {pid}', 
                                         shell=True, 
                                         capture_output=True)
                            print(f"    Killed process on port {port}")
            except:
                pass
    else:
        # Linux/Mac
        for port in [8000, 8002, 8003]:
            subprocess.run(f'fuser -k {port}/tcp', 
                          shell=True, 
                          capture_output=True)

def start_services():
    """Start all services"""
    print("\nStarting services...")
    
    services = [
        ("Backend Service", "backend.py", 8002),
        ("ML Service", "ml_backend.py", 8003),
        ("Frontend Server", "-m http.server", 8000)
    ]
    
    processes = []
    
    for name, script, port in services:
        print(f"\nStarting {name} on port {port}...")
        
        try:
            if script.startswith('-m'):
                # Module execution
                cmd = [sys.executable] + script.split() + [str(port)]
            else:
                # Script execution
                cmd = [sys.executable, script, str(port)]
            
            # Start process
            if platform.system() == 'Windows':
                # Windows - create new window
                process = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Linux/Mac
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            processes.append(process)
            time.sleep(2)  # Wait for service to start
            
            # Check if service started
            if process.poll() is None:
                print(f"    ✓ {name} started successfully")
            else:
                print(f"    ⚠ {name} may have failed to start")
                
        except Exception as e:
            print(f"    ✗ Error starting {name}: {e}")
    
    return processes

def main():
    """Main execution"""
    print("\n" + "="*70)
    print("    STOCK TRACKER - SIMPLE STARTUP")
    print("="*70)
    
    # Check Python
    if not check_python():
        input("\nPress Enter to exit...")
        return
    
    # Check if packages need to be installed
    try:
        import fastapi
        import uvicorn
        import yfinance
        print("\n✓ Packages already installed, skipping installation")
    except ImportError:
        install_packages()
    
    # Kill existing processes
    kill_existing_processes()
    
    # Start services
    processes = start_services()
    
    print("\n" + "="*70)
    print("    STOCK TRACKER IS READY!")
    print("="*70)
    print("\nServices running at:")
    print("  - Web Interface: http://localhost:8000")
    print("  - Backend API:   http://localhost:8002/docs")
    print("  - ML Service:    http://localhost:8003/docs")
    
    # Open browser
    print("\nOpening browser...")
    time.sleep(2)
    webbrowser.open('http://localhost:8000')
    
    print("\n⚠ Keep this window open!")
    print("Press Ctrl+C to stop all services and exit.")
    print("\n" + "="*70 + "\n")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            for process in processes:
                if process.poll() is not None:
                    print(f"\n⚠ Warning: A service has stopped. Restarting may be needed.")
    except KeyboardInterrupt:
        print("\n\nStopping all services...")
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        print("All services stopped. Goodbye!")

if __name__ == "__main__":
    main()
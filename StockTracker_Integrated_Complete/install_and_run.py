#!/usr/bin/env python3
"""
Stock Tracker - Python Installation and Startup Script
Fallback option if batch files don't work
"""

import subprocess
import sys
import os
import time
import webbrowser
import threading
import signal

def install_requirements():
    """Install required packages"""
    print("\n" + "="*70)
    print("    INSTALLING REQUIRED PACKAGES")
    print("="*70 + "\n")
    
    packages = [
        ('pip', 'pip'),
        ('FastAPI', 'fastapi'),
        ('Uvicorn', 'uvicorn'),
        ('Yahoo Finance', 'yfinance'),
        ('Pandas', 'pandas'),
        ('NumPy', 'numpy'),
        ('Timezone Support', 'pytz'),
        ('File Upload', 'python-multipart'),
        ('Async Files', 'aiofiles'),
    ]
    
    for name, package in packages:
        print(f"Installing {name}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', '--upgrade', package])
            print(f"✓ {name} installed")
        except:
            print(f"⚠ {name} installation failed (may already be installed)")
    
    print("\n✓ Package installation complete!\n")

def check_port(port):
    """Check if a port is in use"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def kill_process_on_port(port):
    """Kill process using a specific port (Windows)"""
    if sys.platform == 'win32':
        try:
            # Get the PID using the port
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
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                        print(f"Killed process on port {port}")
                        break
        except:
            pass

def start_service(name, command, port):
    """Start a service in the background"""
    print(f"Starting {name} on port {port}...")
    
    # Kill any existing process on the port
    if check_port(port):
        kill_process_on_port(port)
        time.sleep(1)
    
    # Start the new process
    if sys.platform == 'win32':
        subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(command, shell=True)
    
    # Wait for service to start
    time.sleep(3)
    
    # Check if service started
    if check_port(port):
        print(f"✓ {name} started successfully on port {port}")
    else:
        print(f"⚠ {name} may have failed to start on port {port}")

def main():
    """Main execution"""
    print("\n" + "="*70)
    print("    STOCK TRACKER - INSTALLATION AND STARTUP")
    print("="*70)
    
    # Check if packages need to be installed
    install_flag = '.installed'
    if not os.path.exists(install_flag):
        install_requirements()
        # Create installation flag
        with open(install_flag, 'w') as f:
            f.write(f"Installed on {time.ctime()}")
    else:
        print("\nPackages already installed. Skipping installation...")
    
    print("\n" + "="*70)
    print("    STARTING SERVICES")
    print("="*70 + "\n")
    
    # Start services
    services = [
        ("Backend Service", f"{sys.executable} backend.py 8002", 8002),
        ("ML Service", f"{sys.executable} ml_backend.py 8003", 8003),
        ("Web Interface", f"{sys.executable} -m http.server 8000", 8000),
    ]
    
    for name, command, port in services:
        start_service(name, command, port)
    
    print("\n" + "="*70)
    print("    STOCK TRACKER IS READY!")
    print("="*70)
    print("\nServices running at:")
    print("  - Web Interface: http://localhost:8000")
    print("  - Backend API:   http://localhost:8002/docs")
    print("  - ML Service:    http://localhost:8003/docs")
    print("\nOpening browser...")
    
    # Open browser
    time.sleep(2)
    webbrowser.open('http://localhost:8000')
    
    print("\n⚠ IMPORTANT: Keep this window open!")
    print("Press Ctrl+C to stop all services and exit.")
    print("\n" + "="*70 + "\n")
    
    # Keep running
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\nStopping all services...")
        # Kill services on exit
        for _, _, port in services:
            kill_process_on_port(port)
        print("All services stopped. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Start all Stock Tracker services with ML Integration Bridge
Maintains backward compatibility while enabling new integration features
"""

import subprocess
import time
import sys
import os
import signal
import requests
from datetime import datetime

# Service configurations
SERVICES = {
    "Frontend": {
        "command": ["python3", "-m", "http.server", "8000"],
        "port": 8000,
        "url": "http://localhost:8000",
        "required": True
    },
    "Main Backend": {
        "command": ["python3", "StockTracker_Complete/backend.py"],
        "port": 8002,
        "url": "http://localhost:8002/api/status",
        "required": True
    },
    "ML Backend": {
        "command": ["python3", "StockTracker_Complete/ml_backend.py"],
        "port": 8003,
        "url": "http://localhost:8003/api/health",
        "required": True
    },
    "Integration Bridge": {
        "command": ["python3", "integration_bridge.py"],
        "port": 8004,
        "url": "http://localhost:8004/api/bridge/health",
        "required": False  # Optional - system works without it
    }
}

processes = []

def signal_handler(sig, frame):
    """Handle shutdown gracefully"""
    print("\n⚠️  Shutting down services...")
    for process, name in processes:
        try:
            process.terminate()
            print(f"  ✅ Stopped {name}")
        except:
            pass
    sys.exit(0)

def check_port(port):
    """Check if a port is already in use"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def wait_for_service(url, timeout=30):
    """Wait for a service to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code in [200, 404]:  # 404 is ok for root endpoints
                return True
        except:
            pass
        time.sleep(1)
    return False

def start_service(name, config):
    """Start a single service"""
    try:
        # Check if already running
        if check_port(config["port"]):
            print(f"  ⚠️  {name} already running on port {config['port']}")
            return None
        
        # Start the service
        print(f"  🚀 Starting {name} on port {config['port']}...")
        process = subprocess.Popen(
            config["command"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for service to be ready
        if wait_for_service(config["url"], timeout=15):
            print(f"  ✅ {name} ready on port {config['port']}")
            return process
        else:
            process.terminate()
            print(f"  ❌ {name} failed to start")
            return None
            
    except Exception as e:
        print(f"  ❌ Error starting {name}: {str(e)}")
        return None

def main():
    """Main startup sequence"""
    print("\n" + "="*60)
    print("🚀 Stock Tracker Complete System Startup")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*60)
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    print("-"*60)
    
    # Start services
    failed_required = []
    
    for name, config in SERVICES.items():
        process = start_service(name, config)
        if process:
            processes.append((process, name))
        elif config["required"]:
            failed_required.append(name)
    
    print("-"*60)
    
    # Check if all required services started
    if failed_required:
        print(f"\n❌ Failed to start required services: {', '.join(failed_required)}")
        print("Shutting down all services...")
        for process, name in processes:
            process.terminate()
        sys.exit(1)
    
    # Display status
    print("\n" + "="*60)
    print("✅ SYSTEM READY")
    print("="*60)
    print("\n📊 Service URLs:")
    print(f"  • Dashboard:         http://localhost:8000")
    print(f"  • Main Backend API:  http://localhost:8002")
    print(f"  • ML Backend API:    http://localhost:8003")
    
    if any(name == "Integration Bridge" for _, name in processes):
        print(f"  • Integration Bridge: http://localhost:8004")
        print("\n✨ ML Integration Features ENABLED")
        print("  • Modules can now share data with ML")
        print("  • ML learns from all module discoveries")
        print("  • Enhanced predictions available")
    else:
        print("\n⚠️  ML Integration Bridge not running")
        print("  • System works normally without integration")
        print("  • To enable: Ensure integration_bridge.py exists")
    
    print("\n📝 Integration Instructions:")
    print("  • View examples: http://localhost:8000/module_integration_examples.html")
    print("  • Client library: ml_integration_client.js")
    print("  • All integrations are OPTIONAL")
    print("  • Modules work normally without integration")
    
    print("\n⌨️  Press Ctrl+C to stop all services")
    print("="*60)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            # Periodic health check
            for process, name in processes:
                if process.poll() is not None:
                    print(f"\n⚠️  {name} has stopped unexpectedly")
                    # Don't exit if Integration Bridge stops (it's optional)
                    if name != "Integration Bridge":
                        print("Shutting down all services...")
                        for p, n in processes:
                            if p != process:
                                p.terminate()
                        sys.exit(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
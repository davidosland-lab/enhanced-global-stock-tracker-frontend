#!/usr/bin/env python3
"""
Complete System Startup Script
Starts all backend services and serves existing HTML modules
Preserves all working functionality while adding missing pieces
"""

import os
import sys
import time
import subprocess
import threading
import signal
import json
from pathlib import Path

# Service configuration
SERVICES = [
    # Core existing services (keep these as they work)
    {
        "name": "Main Orchestrator",
        "file": "orchestrator_enhanced.py",
        "port": 8000,
        "required": True,
        "check_endpoint": "/"
    },
    {
        "name": "ML Backend with FinBERT",
        "file": "StockTracker_V10_Windows11_Clean/ml_backend_enhanced_finbert.py",
        "port": 8002,
        "required": True,
        "check_endpoint": "/health"
    },
    {
        "name": "FinBERT Document Analyzer",
        "file": "StockTracker_V10_Windows11_Clean/finbert_backend.py",
        "port": 8003,
        "required": True,
        "check_endpoint": "/health"
    },
    {
        "name": "Historical Data SQLite",
        "file": "StockTracker_V10_Windows11_Clean/historical_backend_sqlite.py",
        "port": 8004,
        "required": True,
        "check_endpoint": "/health"
    },
    {
        "name": "Backtesting Enhanced",
        "file": "StockTracker_V10_Windows11_Clean/backtesting_enhanced.py",
        "port": 8005,
        "required": True,
        "check_endpoint": "/health"
    },
    {
        "name": "Global Sentiment Scraper",
        "file": "StockTracker_V10_Windows11_Clean/enhanced_global_scraper.py",
        "port": 8006,
        "required": True,
        "check_endpoint": "/health"
    },
    # New services for missing modules
    {
        "name": "Indices Tracker",
        "file": "indices_tracker_backend.py",
        "port": 8007,
        "required": False,
        "check_endpoint": "/"
    },
    {
        "name": "Performance Tracker",
        "file": "performance_tracker_backend.py",
        "port": 8010,
        "required": False,
        "check_endpoint": "/"
    }
]

# Track running processes
processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nShutting down services...")
    for proc in processes:
        if proc and proc.poll() is None:
            proc.terminate()
            time.sleep(0.5)
            if proc.poll() is None:
                proc.kill()
    sys.exit(0)

def check_port_available(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def start_service(service):
    """Start a single service"""
    if not os.path.exists(service["file"]):
        print(f"❌ {service['name']}: File not found ({service['file']})")
        return None
    
    if not check_port_available(service["port"]):
        print(f"⚠️  {service['name']}: Port {service['port']} already in use")
        return None
    
    print(f"🚀 Starting {service['name']} on port {service['port']}...")
    
    # Python command
    cmd = [sys.executable, service["file"]]
    
    # Start the process
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        processes.append(proc)
        
        # Give it time to start
        time.sleep(2)
        
        # Check if it's running
        if proc.poll() is None:
            print(f"✅ {service['name']} started successfully")
            return proc
        else:
            print(f"❌ {service['name']} failed to start")
            return None
            
    except Exception as e:
        print(f"❌ {service['name']}: Error starting - {str(e)}")
        return None

def create_module_index():
    """Create an index HTML file that links all modules"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Tracker Complete System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            font-size: 3em;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .modules-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .module-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        .module-card:hover {
            transform: translateY(-5px);
        }
        .module-title {
            font-size: 1.5em;
            color: #667eea;
            margin-bottom: 10px;
        }
        .module-description {
            color: #666;
            margin-bottom: 15px;
        }
        .module-link {
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: transform 0.2s;
        }
        .module-link:hover {
            transform: scale(1.05);
        }
        .status-panel {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .service-status {
            display: flex;
            align-items: center;
            margin: 10px 0;
        }
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .status-online {
            background: #48bb78;
        }
        .status-offline {
            background: #f56565;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Stock Tracker Complete System</h1>
        
        <div class="status-panel">
            <h2>System Status</h2>
            <div id="serviceStatus"></div>
        </div>
        
        <div class="modules-grid">
            <div class="module-card">
                <div class="module-title">🎯 Prediction Center</div>
                <div class="module-description">ML-powered stock predictions with FinBERT sentiment</div>
                <a href="prediction_center_fixed.html" class="module-link">Open Module</a>
            </div>
            
            <div class="module-card">
                <div class="module-title">🌍 Global Market Tracker</div>
                <div class="module-description">Track global indices and market movements</div>
                <a href="global_market_tracker.html" class="module-link">Open Module</a>
            </div>
            
            <div class="module-card">
                <div class="module-title">📈 Indices Tracker</div>
                <div class="module-description">AORD, FTSE, S&P 500 and major indices</div>
                <a href="indices_tracker_fixed_times.html" class="module-link">Open Module</a>
            </div>
            
            <div class="module-card">
                <div class="module-title">🏦 CBA Enhanced Analysis</div>
                <div class="module-description">Commonwealth Bank and ASX analysis</div>
                <a href="cba_enhanced.html" class="module-link">Open Module</a>
            </div>
            
            <div class="module-card">
                <div class="module-title">📊 Technical Analysis</div>
                <div class="module-description">Advanced charts and technical indicators</div>
                <a href="technical_analysis_enhanced.html" class="module-link">Open Module</a>
            </div>
            
            <div class="module-card">
                <div class="module-title">🎭 Sentiment Analysis</div>
                <div class="module-description">Global sentiment from news and social media</div>
                <a href="sentiment_scraper_universal.html" class="module-link">Open Module</a>
            </div>
            
            <div class="module-card">
                <div class="module-title">📉 Historical Analysis</div>
                <div class="module-description">Historical data analysis with patterns</div>
                <a href="historical_data_analysis.html" class="module-link">Open Module</a>
            </div>
            
            <div class="module-card">
                <div class="module-title">🎯 Performance Tracker</div>
                <div class="module-description">Track model and prediction performance</div>
                <a href="performance_tracker.html" class="module-link">Open Module</a>
            </div>
            
            <div class="module-card">
                <div class="module-title">📄 Document Analyzer</div>
                <div class="module-description">Analyze documents with FinBERT</div>
                <a href="document_analyzer.html" class="module-link">Open Module</a>
            </div>
            
            <div class="module-card">
                <div class="module-title">🔄 Backtesting</div>
                <div class="module-description">Test strategies with historical data</div>
                <a href="backtesting.html" class="module-link">Open Module</a>
            </div>
        </div>
    </div>
    
    <script>
        async function checkServices() {
            const services = [
                { name: "Orchestrator", port: 8000 },
                { name: "ML Backend", port: 8002 },
                { name: "FinBERT", port: 8003 },
                { name: "Historical Data", port: 8004 },
                { name: "Backtesting", port: 8005 },
                { name: "Sentiment Scraper", port: 8006 },
                { name: "Indices Tracker", port: 8007 },
                { name: "Performance Tracker", port: 8010 }
            ];
            
            const statusDiv = document.getElementById('serviceStatus');
            statusDiv.innerHTML = '';
            
            for (const service of services) {
                try {
                    const response = await fetch(`http://localhost:${service.port}/`, { 
                        mode: 'no-cors',
                        signal: AbortSignal.timeout(1000)
                    });
                    statusDiv.innerHTML += `
                        <div class="service-status">
                            <div class="status-indicator status-online"></div>
                            ${service.name} (Port ${service.port}): Online
                        </div>`;
                } catch (error) {
                    statusDiv.innerHTML += `
                        <div class="service-status">
                            <div class="status-indicator status-offline"></div>
                            ${service.name} (Port ${service.port}): Offline
                        </div>`;
                }
            }
        }
        
        checkServices();
        setInterval(checkServices, 30000); // Check every 30 seconds
    </script>
</body>
</html>"""
    
    with open("system_index.html", "w") as f:
        f.write(html_content)
    print("✅ Created system index at system_index.html")

def main():
    """Main startup function"""
    print("=" * 60)
    print("STOCK TRACKER COMPLETE SYSTEM STARTUP")
    print("=" * 60)
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create index page
    create_module_index()
    
    # Start all services
    successful_starts = 0
    failed_starts = 0
    
    for service in SERVICES:
        proc = start_service(service)
        if proc:
            successful_starts += 1
        elif service["required"]:
            failed_starts += 1
            print(f"⚠️  Warning: Required service {service['name']} failed to start")
    
    print("\n" + "=" * 60)
    print(f"STARTUP COMPLETE")
    print(f"✅ Successfully started: {successful_starts} services")
    if failed_starts > 0:
        print(f"❌ Failed to start: {failed_starts} services")
    print("=" * 60)
    
    # Provide access instructions
    print("\n📊 ACCESS YOUR SYSTEM:")
    print("=" * 60)
    print("🌐 Main Dashboard: http://localhost:8000/system_index.html")
    print("🎯 Prediction Center: http://localhost:8000/prediction_center_fixed.html")
    print("🌍 Global Markets: http://localhost:8000/global_market_tracker.html")
    print("📈 Indices Tracker: http://localhost:8000/indices_tracker_fixed_times.html")
    print("🏦 CBA Analysis: http://localhost:8000/cba_enhanced.html")
    print("📊 Technical Analysis: http://localhost:8000/technical_analysis_enhanced.html")
    print("=" * 60)
    
    print("\n⚠️  Press Ctrl+C to stop all services\n")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
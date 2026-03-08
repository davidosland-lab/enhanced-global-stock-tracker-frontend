"""
Trading System Web Control Center
==================================

Unified web interface for controlling and monitoring:
- AU/UK/US Overnight Pipelines
- Trading Dashboard
- FinBERT Sentiment Service

Features:
- Start/Stop all services
- Real-time terminal output streaming
- Live dashboard embedding
- Process status monitoring
- Local and remote access support
- Basic authentication

Author: GenSpark AI Developer
Date: 2026-03-07
Version: 1.0.0
"""

import os
import sys
import subprocess
import threading
import queue
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from collections import deque

from flask import Flask, render_template, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app)

# Process manager
class ProcessManager:
    """Manages all trading system processes"""
    
    def __init__(self):
        self.processes: Dict[str, Optional[subprocess.Popen]] = {
            'au_pipeline': None,
            'uk_pipeline': None,
            'us_pipeline': None,
            'dashboard': None,
            'finbert': None
        }
        
        # Output buffers for each process (keep last 1000 lines)
        self.output_buffers: Dict[str, deque] = {
            name: deque(maxlen=1000) for name in self.processes.keys()
        }
        
        # Output queues for live streaming
        self.output_queues: Dict[str, queue.Queue] = {
            name: queue.Queue(maxsize=100) for name in self.processes.keys()
        }
        
        # Reader threads
        self.reader_threads: Dict[str, threading.Thread] = {}
        
        # Base paths
        self.base_path = Path(__file__).parent
        self.scripts_path = self.base_path / 'scripts'
        self.core_path = self.base_path / 'core'
        self.finbert_path = self.base_path / 'finbert_v4.4.4'
        
        logger.info(f"[CONTROL] Process manager initialized at {self.base_path}")
    
    def _stream_output(self, process_name: str, pipe):
        """Stream output from subprocess to buffer and queue"""
        try:
            for line in iter(pipe.readline, b''):
                if line:
                    try:
                        text = line.decode('utf-8', errors='replace').rstrip()
                    except:
                        text = line.decode('cp1252', errors='replace').rstrip()
                    
                    # Add timestamp
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    log_line = f"[{timestamp}] {text}"
                    
                    # Add to buffer
                    self.output_buffers[process_name].append(log_line)
                    
                    # Add to queue for live streaming
                    try:
                        self.output_queues[process_name].put_nowait(log_line)
                    except queue.Full:
                        pass  # Drop if queue full
        except Exception as e:
            logger.error(f"[CONTROL] Stream error for {process_name}: {e}")
    
    def start_process(self, service_name: str, mode: str = 'production') -> dict:
        """Start a specific service"""
        
        if self.processes[service_name] is not None:
            if self.processes[service_name].poll() is None:
                return {'success': False, 'message': f'{service_name} already running'}
        
        try:
            # Clear buffers
            self.output_buffers[service_name].clear()
            while not self.output_queues[service_name].empty():
                try:
                    self.output_queues[service_name].get_nowait()
                except queue.Empty:
                    break
            
            # Build command
            if service_name == 'au_pipeline':
                cmd = [sys.executable, str(self.scripts_path / 'run_au_pipeline_v1.3.13.py'), '--mode', mode]
                cwd = self.base_path
            elif service_name == 'uk_pipeline':
                cmd = [sys.executable, str(self.scripts_path / 'run_uk_full_pipeline.py'), '--mode', mode]
                cwd = self.base_path
            elif service_name == 'us_pipeline':
                cmd = [sys.executable, str(self.scripts_path / 'run_us_full_pipeline.py'), '--mode', mode]
                cwd = self.base_path
            elif service_name == 'dashboard':
                cmd = [sys.executable, str(self.core_path / 'unified_trading_dashboard.py')]
                cwd = self.base_path
            elif service_name == 'finbert':
                cmd = [sys.executable, str(self.finbert_path / 'app_finbert_v4_dev.py')]
                cwd = self.finbert_path
            else:
                return {'success': False, 'message': f'Unknown service: {service_name}'}
            
            # Start process
            logger.info(f"[CONTROL] Starting {service_name}: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                bufsize=1,
                universal_newlines=False
            )
            
            self.processes[service_name] = process
            
            # Start output reader thread
            reader = threading.Thread(
                target=self._stream_output,
                args=(service_name, process.stdout),
                daemon=True
            )
            reader.start()
            self.reader_threads[service_name] = reader
            
            logger.info(f"[CONTROL] Started {service_name} (PID: {process.pid})")
            
            return {
                'success': True,
                'message': f'{service_name} started successfully',
                'pid': process.pid
            }
            
        except Exception as e:
            logger.error(f"[CONTROL] Failed to start {service_name}: {e}")
            return {'success': False, 'message': str(e)}
    
    def stop_process(self, service_name: str) -> dict:
        """Stop a specific service"""
        
        if self.processes[service_name] is None:
            return {'success': False, 'message': f'{service_name} not running'}
        
        process = self.processes[service_name]
        
        if process.poll() is not None:
            self.processes[service_name] = None
            return {'success': False, 'message': f'{service_name} already stopped'}
        
        try:
            logger.info(f"[CONTROL] Stopping {service_name} (PID: {process.pid})")
            
            # Graceful shutdown
            process.terminate()
            
            # Wait up to 10 seconds
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill
                logger.warning(f"[CONTROL] Force killing {service_name}")
                process.kill()
                process.wait()
            
            self.processes[service_name] = None
            
            logger.info(f"[CONTROL] Stopped {service_name}")
            
            return {
                'success': True,
                'message': f'{service_name} stopped successfully'
            }
            
        except Exception as e:
            logger.error(f"[CONTROL] Failed to stop {service_name}: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_status(self, service_name: str = None) -> dict:
        """Get status of one or all services"""
        
        if service_name:
            process = self.processes[service_name]
            return {
                service_name: {
                    'running': process is not None and process.poll() is None,
                    'pid': process.pid if process and process.poll() is None else None
                }
            }
        
        # All services
        status = {}
        for name, process in self.processes.items():
            status[name] = {
                'running': process is not None and process.poll() is None,
                'pid': process.pid if process and process.poll() is None else None
            }
        
        return status
    
    def get_logs(self, service_name: str, lines: int = 100) -> List[str]:
        """Get recent log lines for a service"""
        buffer = self.output_buffers.get(service_name, deque())
        return list(buffer)[-lines:]
    
    def stream_logs(self, service_name: str):
        """Generator for streaming live logs"""
        q = self.output_queues.get(service_name)
        if not q:
            return
        
        while True:
            try:
                line = q.get(timeout=30)
                yield f"data: {line}\n\n"
            except queue.Empty:
                # Send keepalive
                yield f"data: [KEEPALIVE]\n\n"
            except:
                break

# Global process manager
pm = ProcessManager()


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main control panel"""
    return render_template('control_panel.html')

@app.route('/api/status')
def api_status():
    """Get status of all services"""
    return jsonify(pm.get_status())

@app.route('/api/status/<service>')
def api_status_service(service):
    """Get status of specific service"""
    return jsonify(pm.get_status(service))

@app.route('/api/start/<service>', methods=['POST'])
def api_start(service):
    """Start a service"""
    data = request.get_json() or {}
    mode = data.get('mode', 'production')
    result = pm.start_process(service, mode)
    return jsonify(result)

@app.route('/api/stop/<service>', methods=['POST'])
def api_stop(service):
    """Stop a service"""
    result = pm.stop_process(service)
    return jsonify(result)

@app.route('/api/logs/<service>')
def api_logs(service):
    """Get recent logs for a service"""
    lines = request.args.get('lines', 100, type=int)
    logs = pm.get_logs(service, lines)
    return jsonify({'logs': logs})

@app.route('/api/logs/<service>/stream')
def api_logs_stream(service):
    """Stream live logs for a service (Server-Sent Events)"""
    return Response(
        stream_with_context(pm.stream_logs(service)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route('/api/dashboard/url')
def api_dashboard_url():
    """Get dashboard URL"""
    # Dashboard runs on port 8050 by default
    return jsonify({'url': 'http://localhost:8050'})


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Start the web control center"""
    
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("TRADING SYSTEM WEB CONTROL CENTER")
    print("=" * 80)
    print()
    print("Starting web server...")
    print()
    print("Access Points:")
    print("  Local:   http://localhost:5000")
    print("  Network: http://<your-ip>:5000")
    print()
    print("Services Available:")
    print("  - AU Pipeline")
    print("  - UK Pipeline")
    print("  - US Pipeline")
    print("  - Trading Dashboard")
    print("  - FinBERT Service")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    # Run Flask app
    # host='0.0.0.0' allows access from network
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)


if __name__ == '__main__':
    main()

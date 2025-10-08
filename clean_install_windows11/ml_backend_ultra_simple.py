#!/usr/bin/env python3
"""
Ultra Simple ML Backend - Minimal dependencies, guaranteed to work
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime
import random

class MLHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        if self.path == '/health':
            self._set_headers()
            response = {
                "status": "healthy",
                "service": "ML Backend (Ultra Simple)",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/api/ml/status':
            self._set_headers()
            response = {
                "status": "operational",
                "backend_type": "ultra_simple",
                "models_loaded": 2,
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/api/ml/models':
            self._set_headers()
            response = {
                "models": [
                    {
                        "id": "model_001",
                        "name": "Demo LSTM - CBA.AX",
                        "symbol": "CBA.AX",
                        "accuracy": 0.912,
                        "model_type": "lstm"
                    },
                    {
                        "id": "model_002",
                        "name": "Demo GRU - AAPL",
                        "symbol": "AAPL",
                        "accuracy": 0.887,
                        "model_type": "gru"
                    }
                ],
                "count": 2
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path.startswith('/api/ml/training/status/'):
            self._set_headers()
            response = {
                "status": "completed",
                "progress": 100,
                "message": "Training completed (simulated)"
            }
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self._set_headers(404)
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            data = json.loads(post_data) if post_data else {}
        except:
            data = {}
        
        if self.path == '/api/ml/train':
            self._set_headers()
            response = {
                "message": "Training started (simulated)",
                "training_id": f"train_{random.randint(1000, 9999)}",
                "model_id": f"model_{random.randint(1000, 9999)}"
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/api/ml/predict':
            self._set_headers()
            symbol = data.get('symbol', 'CBA.AX')
            base_price = 170 if symbol == 'CBA.AX' else 100
            
            response = {
                "symbol": symbol,
                "current_price": base_price,
                "predictions": {
                    "lstm": base_price * (1 + random.uniform(-0.05, 0.15)),
                    "random_forest": base_price * (1 + random.uniform(-0.05, 0.15))
                },
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self._set_headers(404)
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        # Override to show logs
        print(f"{self.log_date_time_string()} - {format%args}")

def run_server(port=8003):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MLHandler)
    print(f"""
============================================================
ML Backend (Ultra Simple) - Starting on port {port}
============================================================
This is a minimal HTTP server implementation with no
external dependencies beyond Python standard library.

Endpoints available:
  GET  /health                     - Health check
  GET  /api/ml/status              - ML status
  GET  /api/ml/models              - List models
  GET  /api/ml/training/status/:id - Training status
  POST /api/ml/train               - Start training
  POST /api/ml/predict             - Make prediction

Server running at: http://localhost:{port}
Press Ctrl+C to stop
============================================================
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == '__main__':
    run_server(8003)
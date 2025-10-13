#!/usr/bin/env python3
"""
Simple HTTP server to serve the Stock Tracker V3 frontend
Serves HTML files and handles CORS for API calls
"""

import http.server
import socketserver
import os
import sys

# Change to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        # Suppress logs or customize as needed
        sys.stdout.write(f"{self.log_date_time_string()} - {format%args}\n")
        sys.stdout.flush()

print(f"""
================================================================================
    STOCK TRACKER V3 - FRONTEND SERVER
================================================================================

Starting frontend server on port {PORT}...
Access the application at: http://localhost:{PORT}

Available pages:
- Main Dashboard: http://localhost:{PORT}/index.html
- Document Analyzer: http://localhost:{PORT}/modules/document_analyzer.html
- Historical Data: http://localhost:{PORT}/modules/historical_data_module.html
- ML Training: http://localhost:{PORT}/modules/ml_training_centre.html
- Prediction Centre: http://localhost:{PORT}/modules/prediction_centre.html

Backend services should be running on:
- Main Backend: http://localhost:8002
- ML Backend: http://localhost:8003
- Integration Bridge: http://localhost:8004

Press Ctrl+C to stop the server.
================================================================================
""")

with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down frontend server...")
        sys.exit(0)
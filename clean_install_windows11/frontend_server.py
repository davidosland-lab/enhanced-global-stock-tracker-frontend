#!/usr/bin/env python3
"""
Frontend HTTP Server for Stock Tracker
Serves static files and handles module loading properly
Runs on port 8000
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse, parse_qs

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow cross-origin requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Prevent caching for development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        # Custom logging format
        sys.stdout.write(f"[Frontend] {self.address_string()} - {format%args}\n")
        sys.stdout.flush()

def run_server(port=8000):
    """Start the frontend HTTP server"""
    try:
        # Change to the directory containing the frontend files
        if os.path.exists('modules'):
            print(f"✓ Found modules directory")
        
        Handler = CustomHTTPRequestHandler
        
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"""
╔══════════════════════════════════════════════════════════╗
║        STOCK TRACKER FRONTEND SERVER                      ║
╠══════════════════════════════════════════════════════════╣
║  Status:  RUNNING                                         ║
║  Port:    {port}                                              ║
║  URL:     http://localhost:{port}                             ║
║                                                            ║
║  Access the application at:                               ║
║  → http://localhost:{port}/index.html                         ║
║                                                            ║
║  Modules are now properly served via HTTP                 ║
║  No more 'file://' security errors!                       ║
║                                                            ║
║  Press Ctrl+C to stop the server                          ║
╚══════════════════════════════════════════════════════════╝
            """)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Frontend server stopped gracefully")
        sys.exit(0)
    except OSError as e:
        if e.errno == 98 or e.errno == 10048:  # Address already in use (Linux/Windows)
            print(f"❌ Error: Port {port} is already in use!")
            print(f"   Try running: netstat -ano | findstr :{port}")
            print(f"   Then kill the process using that port")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Allow custom port via command line
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
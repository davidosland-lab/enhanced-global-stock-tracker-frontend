"""
Simple Static File Server for Stock Tracker Frontend
This serves the HTML files while the backend API runs on port 8002
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys
import threading
import time
import webbrowser

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def serve_frontend(port=8080):
    """Serve the frontend files on specified port"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    
    print(f"""
    ============================================
    Stock Tracker Frontend Server
    ============================================
    
    Frontend URL: http://localhost:{port}
    Backend API: http://localhost:8002
    
    Open your browser to: http://localhost:{port}
    ============================================
    """)
    
    # Open browser after 2 seconds
    def open_browser():
        time.sleep(2)
        webbrowser.open(f'http://localhost:{port}')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down frontend server...")
        httpd.shutdown()

if __name__ == "__main__":
    # Check if backend is running
    import urllib.request
    try:
        urllib.request.urlopen('http://localhost:8002')
        print("✅ Backend detected on port 8002")
    except:
        print("⚠️ Warning: Backend not detected on port 8002")
        print("Make sure to run: python backend.py")
    
    serve_frontend(8080)
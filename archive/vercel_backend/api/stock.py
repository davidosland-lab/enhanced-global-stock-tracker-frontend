"""
Vercel Serverless Function for stock data
Deploy this to Vercel for a serverless backend
"""

from http.server import BaseHTTPRequestHandler
import json
import yfinance as yf
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL and query parameters
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # Extract symbol from path (expecting /api/stock/SYMBOL format)
        path_parts = parsed_path.path.split('/')
        if len(path_parts) < 4:
            self.send_error(400, "Invalid path. Use /api/stock/SYMBOL")
            return
            
        symbol = path_parts[3]  # Get symbol from path
        period = query_params.get('period', ['5d'])[0]
        interval = query_params.get('interval', ['5m'])[0]
        
        try:
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"No data for {symbol}"}).encode())
                return
            
            # Prepare response data
            data_points = []
            for timestamp, row in hist.iterrows():
                data_points.append({
                    "timestamp": timestamp.isoformat(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })
            
            response = {
                "symbol": symbol,
                "data": data_points,
                "previousClose": float(hist["Close"].iloc[0]) if len(hist) > 0 else None
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
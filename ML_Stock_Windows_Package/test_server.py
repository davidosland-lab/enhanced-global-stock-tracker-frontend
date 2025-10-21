#!/usr/bin/env python3
"""
Simple Test Server - Minimal dependencies for testing
"""

print("Starting test server...")
print("="*50)

import sys
import os

# Print Python info
print(f"Python: {sys.version}")
print(f"CWD: {os.getcwd()}")
print("="*50)

# Test imports one by one
print("\nTesting imports:")

try:
    from flask import Flask, jsonify
    print("✅ Flask imported")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    print("   Install with: pip install flask")
    sys.exit(1)

try:
    from flask_cors import CORS
    print("✅ Flask-CORS imported")
except ImportError as e:
    print(f"❌ Flask-CORS import failed: {e}")
    print("   Install with: pip install flask-cors")
    sys.exit(1)

# Create minimal app
print("\nCreating Flask app...")
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Server</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: #f0f0f0;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .status { 
                padding: 10px; 
                background: #4CAF50; 
                color: white; 
                border-radius: 5px; 
                margin: 20px 0;
            }
            button {
                background: #008CBA;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            button:hover {
                background: #006a8a;
            }
            #result {
                margin-top: 20px;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 5px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Test Server is Working!</h1>
            <div class="status">
                ✅ Server is running successfully on port 8000
            </div>
            
            <h2>Quick Tests:</h2>
            <button onclick="testAPI()">Test API</button>
            <button onclick="testYahoo()">Test Yahoo Finance</button>
            <button onclick="checkImports()">Check Imports</button>
            
            <div id="result"></div>
        </div>
        
        <script>
            async function testAPI() {
                try {
                    const response = await fetch('/api/test');
                    const data = await response.json();
                    document.getElementById('result').innerHTML = 
                        '<h3>API Test Result:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        '<h3>Error:</h3><pre>' + error + '</pre>';
                }
            }
            
            async function testYahoo() {
                document.getElementById('result').innerHTML = '<h3>Testing Yahoo Finance...</h3>';
                try {
                    const response = await fetch('/api/yahoo-test');
                    const data = await response.json();
                    document.getElementById('result').innerHTML = 
                        '<h3>Yahoo Finance Test:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        '<h3>Error:</h3><pre>' + error + '</pre>';
                }
            }
            
            async function checkImports() {
                try {
                    const response = await fetch('/api/imports');
                    const data = await response.json();
                    document.getElementById('result').innerHTML = 
                        '<h3>Import Status:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        '<h3>Error:</h3><pre>' + error + '</pre>';
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'success',
        'message': 'API is working!',
        'python_version': sys.version,
        'platform': sys.platform
    })

@app.route('/api/imports')
def api_imports():
    imports = {}
    
    # Test common imports
    modules = ['flask', 'flask_cors', 'yfinance', 'pandas', 'numpy', 'requests']
    
    for module in modules:
        try:
            mod = __import__(module.replace('flask_cors', 'flask_cors'))
            version = getattr(mod, '__version__', 'installed')
            imports[module] = {'status': 'OK', 'version': version}
        except ImportError:
            imports[module] = {'status': 'NOT INSTALLED'}
        except Exception as e:
            imports[module] = {'status': 'ERROR', 'error': str(e)}
    
    return jsonify(imports)

@app.route('/api/yahoo-test')
def api_yahoo_test():
    try:
        import yfinance as yf
        
        # Try to fetch AAPL
        ticker = yf.Ticker("AAPL")
        
        # Try different methods
        results = {}
        
        # Method 1: download
        try:
            df = yf.download("AAPL", period="1d", progress=False, threads=False)
            if not df.empty:
                results['download'] = {
                    'status': 'success',
                    'latest_price': float(df['Close'].iloc[-1])
                }
            else:
                results['download'] = {'status': 'empty'}
        except Exception as e:
            results['download'] = {'status': 'error', 'error': str(e)[:100]}
        
        # Method 2: history
        try:
            hist = ticker.history(period="1d")
            if not hist.empty:
                results['history'] = {
                    'status': 'success',
                    'latest_price': float(hist['Close'].iloc[-1])
                }
            else:
                results['history'] = {'status': 'empty'}
        except Exception as e:
            results['history'] = {'status': 'error', 'error': str(e)[:100]}
        
        # Method 3: info
        try:
            info = ticker.info
            if info:
                results['info'] = {
                    'status': 'success',
                    'company': info.get('longName', 'Unknown'),
                    'price': info.get('regularMarketPrice', 0)
                }
            else:
                results['info'] = {'status': 'empty'}
        except Exception as e:
            results['info'] = {'status': 'error', 'error': str(e)[:100]}
        
        return jsonify({
            'yfinance_available': True,
            'version': yf.__version__,
            'test_results': results
        })
        
    except ImportError:
        return jsonify({
            'yfinance_available': False,
            'error': 'yfinance not installed'
        })
    except Exception as e:
        return jsonify({
            'yfinance_available': True,
            'error': str(e)
        })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Starting server on http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("="*50 + "\n")
    
    try:
        app.run(host='127.0.0.1', port=8000, debug=False)
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        print("\nPossible solutions:")
        print("1. Check if port 8000 is in use")
        print("2. Run as administrator")
        print("3. Check Windows Firewall")
        input("\nPress Enter to exit...")
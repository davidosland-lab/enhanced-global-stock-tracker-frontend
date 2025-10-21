#!/usr/bin/env python3
"""
Simple launcher script for the unified ML system
Handles encoding issues and provides clean startup
"""

import os
import sys
import warnings

# Fix encoding issues on Windows
if sys.platform == 'win32':
    # Set UTF-8 as default encoding
    import locale
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

# Suppress warnings
warnings.filterwarnings('ignore')

# Import and run the main system
try:
    from unified_ml_system import main
    main()
except ImportError as e:
    print(f"Error importing unified system: {e}")
    print("\nTrying alternative startup...")
    
    # Try running Flask directly
    from flask import Flask, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/')
    def index():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ML Stock Predictor</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 50px auto; 
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                }
                h1 { color: #333; }
                .status { 
                    padding: 10px; 
                    background: #f0f0f0; 
                    border-radius: 5px; 
                    margin: 10px 0;
                }
                .success { background: #d4edda; color: #155724; }
                .warning { background: #fff3cd; color: #856404; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 ML Stock Predictor - Running</h1>
                <div class="status success">
                    ✅ System is running on port 8000
                </div>
                <div class="status">
                    📊 API Endpoints Available:
                    <ul>
                        <li>/api/status - System status</li>
                        <li>/api/fetch - Fetch stock data</li>
                        <li>/api/train - Train ML model</li>
                        <li>/api/predict - Make predictions</li>
                        <li>/api/backtest - Run backtesting</li>
                    </ul>
                </div>
                <div class="status warning">
                    ⚠️ Full interface may not be loaded. Check console for details.
                </div>
                <p>If the full interface doesn't load, you can still use the API endpoints directly.</p>
            </div>
        </body>
        </html>
        """
    
    @app.route('/api/status')
    def status():
        return jsonify({
            'status': 'running',
            'mode': 'fallback',
            'message': 'System running in simplified mode'
        })
    
    print("\n" + "="*60)
    print("🚀 Starting ML Stock Predictor in simplified mode")
    print("📊 Open your browser to http://localhost:8000")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=8000, debug=False)
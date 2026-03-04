#!/usr/bin/env python3
"""
Production Regime Dashboard with Authentication
Secure, production-ready web application for regime monitoring

Author: Trading System v1.3.13 - PRODUCTION EDITION
Date: January 6, 2026
"""

import os
import json
import logging
from functools import wraps
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

# Import regime intelligence modules
try:
    from models.market_data_fetcher import MarketDataFetcher
    from models.market_regime_detector import MarketRegimeDetector
    from models.enhanced_data_sources import EnhancedDataSources
    from models.cross_market_features import CrossMarketFeatures
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from models.market_data_fetcher import MarketDataFetcher
    from models.market_regime_detector import MarketRegimeDetector
    from models.enhanced_data_sources import EnhancedDataSources
    from models.cross_market_features import CrossMarketFeatures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# User database (in production, use proper database)
USERS = {
    'admin': generate_password_hash('change_me_in_production'),  # Default password
    # Add more users as needed
}

# Environment-based configuration
PRODUCTION = os.environ.get('PRODUCTION', 'false').lower() == 'true'
DEBUG = not PRODUCTION
PORT = int(os.environ.get('PORT', 5002))
HOST = '0.0.0.0' if PRODUCTION else '127.0.0.1'

# Initialize regime intelligence components
try:
    market_data_fetcher = MarketDataFetcher()
    regime_detector = MarketRegimeDetector()
    enhanced_data = EnhancedDataSources()
    feature_engineer = CrossMarketFeatures()
    logger.info("✅ All regime intelligence components initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize components: {e}")
    market_data_fetcher = None
    regime_detector = None
    enhanced_data = None
    feature_engineer = None


# Authentication decorator
def login_required(f):
    """Require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# ===== AUTHENTICATION ROUTES =====

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username in USERS and check_password_hash(USERS[username], password):
            session['username'] = username
            session.permanent = True
            logger.info(f"✅ User logged in: {username}")
            
            # Redirect to next URL or dashboard
            next_url = request.args.get('next')
            return redirect(next_url or url_for('dashboard'))
        else:
            logger.warning(f"❌ Failed login attempt: {username}")
            return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials")
    
    return render_template_string(LOGIN_TEMPLATE)


@app.route('/logout')
def logout():
    """Logout"""
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"✅ User logged out: {username}")
    return redirect(url_for('login'))


# ===== DASHBOARD ROUTES =====

@app.route('/')
@login_required
def dashboard():
    """Main dashboard (requires authentication)"""
    username = session.get('username', 'User')
    return render_template_string(DASHBOARD_TEMPLATE, username=username)


@app.route('/api/regime-data')
@login_required
def get_regime_data():
    """
    API endpoint to get current regime data (protected)
    
    Returns:
        JSON with market data, regime detection, enhanced data, and sector impacts
    """
    try:
        if not all([market_data_fetcher, regime_detector, enhanced_data, feature_engineer]):
            return jsonify({
                'error': 'Regime intelligence components not initialized',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Fetch market data
        market_data = market_data_fetcher.fetch_overnight_data()
        
        # Get enhanced data
        enhanced_market_data = enhanced_data.get_enhanced_data()
        
        # Detect regime
        regime_result = regime_detector.detect_regime(market_data)
        
        # Format response
        response = {
            'market_data': {
                'sp500_change': market_data.get('sp500_change', 0),
                'nasdaq_change': market_data.get('nasdaq_change', 0),
                'oil_change': market_data.get('oil_change', 0),
                'iron_ore': {
                    'price': enhanced_market_data.get('iron_ore', {}).get('price', 0),
                    'change_pct': enhanced_market_data.get('iron_ore', {}).get('change_pct', 0),
                    'confidence': enhanced_market_data.get('iron_ore', {}).get('confidence', 0),
                    'source': enhanced_market_data.get('iron_ore', {}).get('source', 'Unknown')
                },
                'aud_usd_change': market_data.get('aud_usd_change', 0),
                'usd_index_change': market_data.get('usd_index_change', 0),
                'us_10y_change': market_data.get('us_10y_change', 0),
                'au_10y': {
                    'yield': enhanced_market_data.get('au_10y', {}).get('yield', 0),
                    'change_bps': enhanced_market_data.get('au_10y', {}).get('change_bps', 0),
                    'confidence': enhanced_market_data.get('au_10y', {}).get('confidence', 0),
                    'source': enhanced_market_data.get('au_10y', {}).get('source', 'Unknown')
                },
                'vix_level': market_data.get('vix_level', 0),
                'copper_change': enhanced_market_data.get('copper', {}).get('change_pct', 0),
                'gold_change': enhanced_market_data.get('gold', {}).get('change_pct', 0),
                'asx200_change': enhanced_market_data.get('asx_200', {}).get('change_pct', 0),
            },
            'regime': {
                'primary': regime_result['primary_regime'].value,
                'strength': regime_result['regime_strength'],
                'confidence': regime_result['confidence'],
                'explanation': regime_result['regime_explanation'],
                'secondary_regimes': [r.value for r in regime_result.get('secondary_regimes', [])]
            },
            'sector_impacts': regime_result.get('sector_impacts', {}),
            'timestamp': datetime.now().isoformat(),
            'user': session.get('username', 'Unknown')
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Error fetching regime data: {e}", exc_info=True)
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint (no auth required for monitoring)"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'market_data_fetcher': market_data_fetcher is not None,
            'regime_detector': regime_detector is not None,
            'enhanced_data': enhanced_data is not None,
            'feature_engineer': feature_engineer is not None
        }
    })


# ===== HTML TEMPLATES =====

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Regime Intelligence Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .error {
            background: #fee;
            color: #c00;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .info {
            margin-top: 20px;
            padding: 10px;
            background: #e8f5e9;
            border-radius: 5px;
            font-size: 12px;
            color: #2e7d32;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🔒 Regime Dashboard</h1>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
        {% if not error %}
        <div class="info">
            Default credentials: admin / change_me_in_production<br>
            <strong>Change password in production!</strong>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Regime Intelligence Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .header {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #333;
            font-size: 24px;
        }
        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .user-info span {
            color: #666;
        }
        .logout-btn {
            padding: 8px 16px;
            background: #f44336;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 14px;
            transition: background 0.3s;
        }
        .logout-btn:hover {
            background: #d32f2f;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .card {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 20px;
        }
        .regime-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 18px;
            margin: 10px 0;
        }
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .data-item {
            padding: 15px;
            background: #f5f5f5;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .data-item label {
            display: block;
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }
        .data-item .value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .data-item .change {
            font-size: 14px;
            margin-left: 10px;
        }
        .positive { color: #4caf50; }
        .negative { color: #f44336; }
        .neutral { color: #ff9800; }
        .sector-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .sector-item {
            padding: 10px;
            background: #f5f5f5;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .sector-bar {
            width: 100px;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            position: relative;
            overflow: hidden;
        }
        .sector-fill {
            height: 100%;
            transition: width 0.3s, background 0.3s;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 18px;
        }
        .refresh-btn {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        .refresh-btn:hover {
            background: #5568d3;
        }
        .timestamp {
            color: #999;
            font-size: 12px;
            margin-top: 10px;
        }
        .confidence-meter {
            width: 100%;
            height: 10px;
            background: #e0e0e0;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 5px;
        }
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #f44336, #ff9800, #4caf50);
            transition: width 0.3s;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 Market Regime Intelligence Dashboard</h1>
            <div class="user-info">
                <span>👤 {{ username }}</span>
                <a href="/logout" class="logout-btn">Logout</a>
            </div>
        </div>
        
        <div id="loading" class="card loading">
            Loading regime data...
        </div>
        
        <div id="dashboard" style="display: none;">
            <!-- Regime Card -->
            <div class="card">
                <h2>🎯 Current Market Regime</h2>
                <div id="regime-badge" class="regime-badge"></div>
                <div style="margin-top: 10px;">
                    <label>Strength:</label>
                    <div class="confidence-meter">
                        <div id="strength-bar" class="confidence-fill"></div>
                    </div>
                    <span id="strength-value" style="font-size: 12px; color: #666;"></span>
                </div>
                <div style="margin-top: 10px;">
                    <label>Confidence:</label>
                    <div class="confidence-meter">
                        <div id="confidence-bar" class="confidence-fill"></div>
                    </div>
                    <span id="confidence-value" style="font-size: 12px; color: #666;"></span>
                </div>
                <p id="regime-explanation" style="margin-top: 15px; color: #666; line-height: 1.6;"></p>
            </div>
            
            <!-- Market Data Card -->
            <div class="card">
                <h2>📊 Market Data</h2>
                <div class="data-grid" id="market-data"></div>
            </div>
            
            <!-- Sector Impacts Card -->
            <div class="card">
                <h2>🎨 Sector Impact Forecast</h2>
                <div class="sector-grid" id="sector-impacts"></div>
            </div>
            
            <!-- Controls -->
            <div class="card">
                <button class="refresh-btn" onclick="loadRegimeData()">🔄 Refresh Data</button>
                <span class="timestamp" id="timestamp"></span>
            </div>
        </div>
    </div>
    
    <script>
        let autoRefreshInterval;
        
        async function loadRegimeData() {
            try {
                const response = await fetch('/api/regime-data');
                if (!response.ok) {
                    if (response.status === 401) {
                        window.location.href = '/login';
                        return;
                    }
                    throw new Error('Failed to fetch data');
                }
                
                const data = await response.json();
                updateDashboard(data);
                
                document.getElementById('loading').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('loading').innerHTML = '❌ Error loading data: ' + error.message;
            }
        }
        
        function updateDashboard(data) {
            // Update regime badge
            const regimeBadge = document.getElementById('regime-badge');
            regimeBadge.textContent = data.regime.primary;
            regimeBadge.style.background = getRegimeColor(data.regime.primary);
            regimeBadge.style.color = 'white';
            
            // Update strength and confidence
            document.getElementById('strength-bar').style.width = (data.regime.strength * 100) + '%';
            document.getElementById('strength-value').textContent = (data.regime.strength * 100).toFixed(0) + '%';
            document.getElementById('confidence-bar').style.width = (data.regime.confidence * 100) + '%';
            document.getElementById('confidence-value').textContent = (data.regime.confidence * 100).toFixed(0) + '%';
            
            // Update explanation
            document.getElementById('regime-explanation').textContent = data.regime.explanation;
            
            // Update market data
            const marketDataHTML = `
                <div class="data-item">
                    <label>S&P 500</label>
                    <div class="value">${data.market_data.sp500_change.toFixed(2)}%</div>
                </div>
                <div class="data-item">
                    <label>NASDAQ</label>
                    <div class="value">${data.market_data.nasdaq_change.toFixed(2)}%</div>
                </div>
                <div class="data-item">
                    <label>Oil</label>
                    <div class="value">${data.market_data.oil_change.toFixed(2)}%</div>
                </div>
                <div class="data-item">
                    <label>Iron Ore (${data.market_data.iron_ore.confidence}% conf)</label>
                    <div class="value">$${data.market_data.iron_ore.price.toFixed(2)}
                        <span class="change ${data.market_data.iron_ore.change_pct >= 0 ? 'positive' : 'negative'}">
                            ${data.market_data.iron_ore.change_pct >= 0 ? '+' : ''}${data.market_data.iron_ore.change_pct.toFixed(2)}%
                        </span>
                    </div>
                </div>
                <div class="data-item">
                    <label>AUD/USD</label>
                    <div class="value">${data.market_data.aud_usd_change.toFixed(2)}%</div>
                </div>
                <div class="data-item">
                    <label>USD Index</label>
                    <div class="value">${data.market_data.usd_index_change.toFixed(2)}%</div>
                </div>
                <div class="data-item">
                    <label>US 10Y</label>
                    <div class="value">${data.market_data.us_10y_change.toFixed(0)} bps</div>
                </div>
                <div class="data-item">
                    <label>AU 10Y (${data.market_data.au_10y.confidence}% conf)</label>
                    <div class="value">${data.market_data.au_10y.yield.toFixed(2)}%
                        <span class="change ${data.market_data.au_10y.change_bps >= 0 ? 'positive' : 'negative'}">
                            ${data.market_data.au_10y.change_bps >= 0 ? '+' : ''}${data.market_data.au_10y.change_bps.toFixed(1)} bps
                        </span>
                    </div>
                </div>
                <div class="data-item">
                    <label>Copper</label>
                    <div class="value">${data.market_data.copper_change.toFixed(2)}%</div>
                </div>
                <div class="data-item">
                    <label>Gold</label>
                    <div class="value">${data.market_data.gold_change.toFixed(2)}%</div>
                </div>
                <div class="data-item">
                    <label>ASX 200</label>
                    <div class="value">${data.market_data.asx200_change.toFixed(2)}%</div>
                </div>
                <div class="data-item">
                    <label>VIX</label>
                    <div class="value">${data.market_data.vix_level.toFixed(1)}</div>
                </div>
            `;
            document.getElementById('market-data').innerHTML = marketDataHTML;
            
            // Update sector impacts
            let sectorHTML = '';
            for (const [sector, impact] of Object.entries(data.sector_impacts)) {
                const impactPct = ((impact + 1) / 2) * 100; // Convert -1..1 to 0..100
                const color = impact < -0.3 ? '#f44336' : impact < 0 ? '#ff9800' : impact < 0.3 ? '#9e9e9e' : '#4caf50';
                const label = impact < -0.5 ? '❌' : impact < 0 ? '⚠️' : impact < 0.3 ? '➖' : '✅';
                
                sectorHTML += `
                    <div class="sector-item">
                        <span>${label} ${sector}</span>
                        <div class="sector-bar">
                            <div class="sector-fill" style="width: ${impactPct}%; background: ${color};"></div>
                        </div>
                        <span style="font-weight: bold; color: ${color};">${impact.toFixed(2)}</span>
                    </div>
                `;
            }
            document.getElementById('sector-impacts').innerHTML = sectorHTML;
            
            // Update timestamp
            document.getElementById('timestamp').textContent = 'Last updated: ' + new Date(data.timestamp).toLocaleString();
        }
        
        function getRegimeColor(regime) {
            const colors = {
                'US_TECH_RALLY': '#4caf50',
                'US_RISK_OFF': '#f44336',
                'COMMODITY_STRONG': '#2196f3',
                'COMMODITY_WEAK': '#ff9800',
                'USD_STRENGTH': '#9c27b0',
                'USD_WEAKNESS': '#00bcd4',
                'NEUTRAL': '#9e9e9e'
            };
            return colors[regime] || '#607d8b';
        }
        
        // Auto-refresh every 5 minutes
        function startAutoRefresh() {
            if (autoRefreshInterval) clearInterval(autoRefreshInterval);
            autoRefreshInterval = setInterval(loadRegimeData, 5 * 60 * 1000);
        }
        
        // Initial load
        loadRegimeData();
        startAutoRefresh();
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("PRODUCTION REGIME DASHBOARD STARTING")
    logger.info("=" * 80)
    logger.info(f"Mode: {'PRODUCTION' if PRODUCTION else 'DEVELOPMENT'}")
    logger.info(f"Host: {HOST}")
    logger.info(f"Port: {PORT}")
    logger.info(f"Debug: {DEBUG}")
    logger.info("=" * 80)
    
    if not PRODUCTION:
        logger.warning("⚠️  Running in DEVELOPMENT mode")
        logger.warning("⚠️  Default credentials: admin / change_me_in_production")
        logger.warning("⚠️  Set PRODUCTION=true for production deployment")
    
    app.run(host=HOST, port=PORT, debug=DEBUG)

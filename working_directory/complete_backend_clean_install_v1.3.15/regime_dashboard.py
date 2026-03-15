#!/usr/bin/env python3
"""
Regime Visualization Dashboard - Week 2 Features
Real-time web dashboard for market regime monitoring

Author: Trading System v1.3.13 - REGIME EDITION (Week 2)
Date: January 6, 2026
"""

from flask import Flask, render_template_string, jsonify
import logging
from datetime import datetime
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import regime intelligence modules
try:
    from models.market_data_fetcher import MarketDataFetcher
    from models.market_regime_detector import MarketRegimeDetector
    from models.enhanced_data_sources import EnhancedDataSources
    from models.cross_market_features import CrossMarketFeatures
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    import traceback
    print(f"[!] Warning: Could not import regime modules")
    print(f"Error: {e}")
    print(f"Current path: {Path(__file__).parent}")
    traceback.print_exc()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global instances
market_data_fetcher = None
regime_detector = None
enhanced_sources = None
cross_market_features = None

# Try to initialize components immediately
if MODULES_AVAILABLE:
    try:
        logger.info("Initializing components at module load...")
        market_data_fetcher = MarketDataFetcher()
        regime_detector = MarketRegimeDetector()
        enhanced_sources = EnhancedDataSources()
        cross_market_features = CrossMarketFeatures()
        logger.info("[OK] Components initialized at module load")
    except Exception as e:
        logger.error(f"[X] Failed to initialize components at module load: {e}")
        import traceback
        traceback.print_exc()

def make_json_serializable(obj):
    """
    Convert objects to JSON-serializable format
    Handles Enums, datetime, and other non-serializable types
    """
    from enum import Enum
    from datetime import datetime, date
    
    if isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    else:
        return obj

def initialize_components():
    """Initialize regime intelligence components"""
    global market_data_fetcher, regime_detector, enhanced_sources, cross_market_features
    
    if not MODULES_AVAILABLE:
        logger.error("[X] Regime modules not available")
        return False
    
    try:
        market_data_fetcher = MarketDataFetcher()
        regime_detector = MarketRegimeDetector()
        enhanced_sources = EnhancedDataSources()
        cross_market_features = CrossMarketFeatures()
        logger.info("[OK] All components initialized")
        return True
    except Exception as e:
        logger.error(f"[X] Failed to initialize components: {e}")
        return False

# HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Regime Dashboard - v1.3.13</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card-title {
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .regime-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 1.1em;
            margin: 5px;
            text-transform: uppercase;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        
        .regime-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .regime-secondary {
            background: linear-gradient(135deg, #f093fb, #f5576c);
            color: white;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .metric-label {
            font-weight: 500;
            color: #666;
        }
        
        .metric-value {
            font-weight: 700;
            font-size: 1.1em;
            color: #333;
        }
        
        .positive {
            color: #10b981 !important;
        }
        
        .negative {
            color: #ef4444 !important;
        }
        
        .neutral {
            color: #6b7280 !important;
        }
        
        .confidence-bar {
            width: 100%;
            height: 30px;
            background: #e5e7eb;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }
        
        .sector-impact {
            display: flex;
            align-items: center;
            margin: 8px 0;
        }
        
        .sector-name {
            flex: 1;
            font-weight: 500;
        }
        
        .sector-bar {
            flex: 2;
            height: 20px;
            background: #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
            margin: 0 10px;
        }
        
        .sector-bar-fill {
            height: 100%;
            transition: width 0.5s ease, background-color 0.3s ease;
        }
        
        .sector-value {
            font-weight: 600;
            min-width: 60px;
            text-align: right;
        }
        
        .explanation {
            background: #f0f9ff;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            color: #1e40af;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 1.1em;
            font-weight: 600;
            border-radius: 25px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            display: block;
            margin: 20px auto;
        }
        
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        .refresh-btn:active {
            transform: translateY(0);
        }
        
        .timestamp {
            text-align: center;
            color: white;
            font-size: 0.9em;
            margin-top: 20px;
            opacity: 0.8;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Market Regime Dashboard</h1>
            <p>Real-Time Global Macro Intelligence</p>
        </div>
        
        <button class="refresh-btn" onclick="refreshDashboard()">[~] Refresh Data</button>
        
        <div id="dashboard-content">
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading market regime data...</p>
            </div>
        </div>
        
        <div class="timestamp" id="timestamp"></div>
    </div>
    
    <script>
        let autoRefreshInterval;
        
        async function refreshDashboard() {
            try {
                const response = await fetch('/api/regime-data');
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('dashboard-content').innerHTML = `
                        <div class="card">
                            <div class="card-title">[!] Error</div>
                            <p>${data.error}</p>
                        </div>
                    `;
                    return;
                }
                
                renderDashboard(data);
                updateTimestamp(data.timestamp);
            } catch (error) {
                console.error('Error fetching regime data:', error);
                document.getElementById('dashboard-content').innerHTML = `
                    <div class="card">
                        <div class="card-title">[X] Connection Error</div>
                        <p>Failed to fetch regime data. Please try again.</p>
                    </div>
                `;
            }
        }
        
        function renderDashboard(data) {
            const content = `
                ${renderCurrentRegime(data.regime)}
                ${renderMarketData(data.market_data)}
                ${renderEnhancedData(data.enhanced_data)}
                ${renderSectorImpacts(data.sector_impacts)}
                ${renderCrossMarketFeatures(data.cross_market)}
            `;
            
            document.getElementById('dashboard-content').innerHTML = content;
        }
        
        function renderCurrentRegime(regime) {
            if (!regime) return '';
            
            // Extract values with fallbacks for API response structure
            const regimeType = regime.primary_regime || regime.regime || 'UNKNOWN';
            const confidence = regime.confidence || 0;
            const strength = regime.regime_strength || regime.strength || 0;
            const explanation = regime.regime_explanation || regime.explanation || 'No explanation available';
            
            return `
                <div class="grid">
                    <div class="card">
                        <div class="card-title">[*] Current Regime</div>
                        <div style="text-align: center; margin: 20px 0;">
                            <div class="regime-badge regime-primary">${regimeType}</div>
                        </div>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${confidence * 100}%">
                                Confidence: ${(confidence * 100).toFixed(0)}%
                            </div>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Strength</span>
                            <span class="metric-value">${strength.toFixed(2)}</span>
                        </div>
                        <div class="explanation">
                            ${explanation}
                        </div>
                    </div>
                </div>
            `;
        }
        
        function renderMarketData(market) {
            if (!market) return '';
            
            return `
                <div class="grid">
                    <div class="card">
                        <div class="card-title">[UP] US Markets</div>
                        ${renderMetric('S&P 500', market.sp500_change || market.sp500_return, '%')}
                        ${renderMetric('NASDAQ', market.nasdaq_change || market.nasdaq_return, '%')}
                        ${renderMetric('VIX', market.vix_level, '')}
                    </div>
                    
                    <div class="card">
                        <div class="card-title">🛢️ Commodities</div>
                        ${renderMetric('Iron Ore', market.iron_ore_change, '%')}
                        ${renderMetric('Oil', market.oil_change, '%')}
                        ${market.copper_change !== undefined ? renderMetric('Copper', market.copper_change, '%') : ''}
                    </div>
                    
                    <div class="card">
                        <div class="card-title">💱 FX & Rates</div>
                        ${renderMetric('AUD/USD', market.aud_usd_change || market.audusd_change, '%')}
                        ${renderMetric('USD Index', market.usd_index_change, '%')}
                        ${renderMetric('US 10Y', market.us_10y_change, ' bps')}
                        ${renderMetric('AU 10Y', market.au_10y_change, ' bps')}
                    </div>
                </div>
            `;
        }
        
        function renderEnhancedData(enhanced) {
            if (!enhanced) return '';
            
            const ironOre = enhanced.iron_ore || {};
            const au10y = enhanced.au_10y || {};
            const additional = enhanced.additional || {};
            
            return `
                <div class="grid">
                    <div class="card">
                        <div class="card-title">🏗️ Iron Ore (Enhanced)</div>
                        ${renderMetric('Price', ironOre.price ? `$${ironOre.price.toFixed(2)}/tonne` : 'N/A', '')}
                        ${renderMetric('Change', ironOre.change_1d, '%')}
                        ${renderMetric('Source', ironOre.source || 'N/A', '')}
                        ${renderMetric('Confidence', ironOre.confidence ? `${(ironOre.confidence * 100).toFixed(0)}%` : 'N/A', '')}
                    </div>
                    
                    <div class="card">
                        <div class="card-title">[#] AU 10Y (Enhanced)</div>
                        ${renderMetric('Yield', au10y.yield ? `${au10y.yield.toFixed(2)}%` : 'N/A', '')}
                        ${renderMetric('Change', au10y.change_1d, ' bps')}
                        ${renderMetric('Source', au10y.source || 'N/A', '')}
                        ${renderMetric('Confidence', au10y.confidence ? `${(au10y.confidence * 100).toFixed(0)}%` : 'N/A', '')}
                    </div>
                    
                    ${additional.gold ? `
                    <div class="card">
                        <div class="card-title">✨ Safe Haven</div>
                        ${renderMetric('Gold', additional.gold.price ? `$${additional.gold.price.toFixed(2)}` : 'N/A', '')}
                        ${renderMetric('Change', additional.gold.change, '%')}
                        ${additional.asx200 ? renderMetric('ASX 200', additional.asx200.price ? additional.asx200.price.toFixed(2) : 'N/A', '') : ''}
                    </div>
                    ` : ''}
                </div>
            `;
        }
        
        function renderSectorImpacts(impacts) {
            if (!impacts || Object.keys(impacts).length === 0) return '';
            
            let html = `
                <div class="card" style="grid-column: 1 / -1;">
                    <div class="card-title">[#] Sector Impacts</div>
            `;
            
            // Sort sectors by impact
            const sortedSectors = Object.entries(impacts).sort((a, b) => b[1] - a[1]);
            
            for (const [sector, impact] of sortedSectors) {
                const percentage = impact * 50 + 50; // Map -1 to 1 -> 0% to 100%
                const color = impact > 0.3 ? '#10b981' : impact < -0.3 ? '#ef4444' : '#6b7280';
                
                html += `
                    <div class="sector-impact">
                        <div class="sector-name">${sector}</div>
                        <div class="sector-bar">
                            <div class="sector-bar-fill" style="width: ${percentage}%; background-color: ${color};"></div>
                        </div>
                        <div class="sector-value" style="color: ${color};">
                            ${impact > 0 ? '+' : ''}${impact.toFixed(2)}
                        </div>
                    </div>
                `;
            }
            
            html += `</div>`;
            return html;
        }
        
        function renderCrossMarketFeatures(crossMarket) {
            if (!crossMarket) return '';
            
            return `
                <div class="grid">
                    <div class="card">
                        <div class="card-title">[GLOBE] Cross-Market Features</div>
                        ${renderMetric('ASX Relative Bias', crossMarket.asx_relative_bias, '')}
                        ${renderMetric('USD Pressure', crossMarket.usd_pressure, '')}
                        ${renderMetric('Commodity Momentum', crossMarket.commodity_momentum, '')}
                        ${renderMetric('Risk Appetite', crossMarket.risk_appetite, '')}
                        ${renderMetric('Rate Divergence', crossMarket.rate_divergence, '')}
                    </div>
                </div>
            `;
        }
        
        function renderMetric(label, value, suffix) {
            if (value === undefined || value === null) return '';
            
            // Handle different value types safely
            let numValue, displayValue, className;
            
            if (typeof value === 'string') {
                // If it's already a string (like "N/A"), use it as-is
                displayValue = value;
                className = 'neutral';
            } else if (typeof value === 'number') {
                // If it's a number, format it properly
                numValue = value;
                className = numValue > 0 ? 'positive' : numValue < 0 ? 'negative' : 'neutral';
                displayValue = (value > 0 ? '+' : '') + value.toFixed(2) + suffix;
            } else {
                // Try to parse it as a number
                numValue = parseFloat(value);
                if (isNaN(numValue)) {
                    displayValue = value;
                    className = 'neutral';
                } else {
                    className = numValue > 0 ? 'positive' : numValue < 0 ? 'negative' : 'neutral';
                    displayValue = (numValue > 0 ? '+' : '') + numValue.toFixed(2) + suffix;
                }
            }
            
            return `
                <div class="metric">
                    <span class="metric-label">${label}</span>
                    <span class="metric-value ${className}">${displayValue}</span>
                </div>
            `;
        }
        
        function updateTimestamp(timestamp) {
            const elem = document.getElementById('timestamp');
            if (timestamp) {
                const date = new Date(timestamp);
                elem.textContent = `Last Updated: ${date.toLocaleString()}`;
            }
        }
        
        // Initial load
        refreshDashboard();
        
        // Auto-refresh every 5 minutes
        autoRefreshInterval = setInterval(refreshDashboard, 5 * 60 * 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/regime-data')
def get_regime_data():
    """API endpoint for regime data"""
    
    if not MODULES_AVAILABLE:
        return jsonify({
            'error': 'Regime modules not available',
            'timestamp': datetime.now().isoformat()
        })
    
    # Check if components are initialized
    if market_data_fetcher is None:
        logger.error("[X] market_data_fetcher is None - components not initialized")
        return jsonify({
            'error': 'Components not initialized. Please restart the dashboard.',
            'timestamp': datetime.now().isoformat()
        })
    
    try:
        # Fetch market data
        market_data = market_data_fetcher.fetch_market_data()
        
        # Fetch enhanced data
        enhanced_data = enhanced_sources.get_all_enhanced_data()
        
        # Update market data with enhanced sources
        if enhanced_data.get('iron_ore', {}).get('change_1d') is not None:
            market_data['iron_ore_change'] = enhanced_data['iron_ore']['change_1d']
        
        if enhanced_data.get('au_10y', {}).get('change_1d') is not None:
            market_data['au_10y_change'] = enhanced_data['au_10y']['change_1d']
        
        # Detect regime
        regime_data = regime_detector.detect_regime(market_data)
        
        # Calculate cross-market features (for one stock as example)
        try:
            cross_market = cross_market_features.calculate_features(market_data)
        except:
            cross_market = {}
        
        # Prepare response
        response = {
            'regime': regime_data,
            'market_data': market_data,
            'enhanced_data': enhanced_data,
            'sector_impacts': regime_data.get('sector_impacts', {}),
            'cross_market': cross_market,
            'timestamp': datetime.now().isoformat()
        }
        
        # Make all data JSON-serializable (handles Enums, datetime, etc.)
        response = make_json_serializable(response)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"[X] Error in API endpoint: {e}", exc_info=True)
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

def main():
    """Main function"""
    print("\n" + "="*80)
    print("🧠 MARKET REGIME VISUALIZATION DASHBOARD")
    print("="*80)
    print("\nStarting dashboard server...")
    
    # Initialize components
    if not initialize_components():
        print("[X] Failed to initialize components")
        return
    
    print("\n[OK] Dashboard ready!")
    print("\n[#] Access the dashboard at:")
    print("   http://localhost:5002")
    print("\n[!] Features:")
    print("   - Real-time regime detection")
    print("   - Enhanced data sources (Iron Ore, AU 10Y)")
    print("   - Sector impact visualization")
    print("   - Cross-market feature display")
    print("   - Auto-refresh every 5 minutes")
    print("\n" + "="*80)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run Flask app (without loading .env to avoid encoding issues)
    import os
    os.environ['FLASK_SKIP_DOTENV'] = '1'
    app.run(host='0.0.0.0', port=5002, debug=False, load_dotenv=False)

if __name__ == "__main__":
    main()

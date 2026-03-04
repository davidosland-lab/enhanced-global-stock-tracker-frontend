"""
Live Trading Dashboard with Intraday Monitoring
===============================================

Real-time monitoring dashboard for the integrated swing trading + intraday system.
Built with Flask and real-time updates.

Features:
- Real-time position tracking
- Performance metrics
- Market sentiment indicators
- Alert history
- Risk exposure monitoring
- Trade history

Author: FinBERT Enhanced System
Version: 2.0
Date: December 21, 2024
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import threading
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global state (would be replaced with actual coordinator in production)
DASHBOARD_STATE = {
    'coordinator': None,  # Will be set by main application
    'last_update': None,
    'alerts': [],
    'performance_history': []
}


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """
    Get current system status
    
    Returns:
        JSON with portfolio status, positions, and metrics
    """
    try:
        coordinator = DASHBOARD_STATE.get('coordinator')
        
        if coordinator is None:
            return jsonify({
                'error': 'Trading coordinator not initialized',
                'status': 'offline'
            })
        
        # Get portfolio status
        portfolio_status = coordinator.get_portfolio_status()
        
        # Get position details
        positions = coordinator.get_position_details()
        
        # Get market context
        market_context = {
            'sentiment_score': coordinator.last_market_sentiment or 50,
            'macro_score': coordinator.last_macro_sentiment or 50,
            'market_open': coordinator.intraday_manager.is_market_open()
        }
        
        # Get intraday stats
        intraday_stats = coordinator.intraday_manager.get_session_stats()
        
        DASHBOARD_STATE['last_update'] = datetime.now().isoformat()
        
        return jsonify({
            'status': 'online',
            'timestamp': DASHBOARD_STATE['last_update'],
            'portfolio': portfolio_status,
            'positions': positions,
            'market_context': market_context,
            'intraday_stats': intraday_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/api/positions')
def get_positions():
    """
    Get detailed position information
    
    Returns:
        JSON with all open positions
    """
    try:
        coordinator = DASHBOARD_STATE.get('coordinator')
        
        if coordinator is None:
            return jsonify({'error': 'Trading coordinator not initialized'})
        
        positions = coordinator.get_position_details()
        
        return jsonify({
            'positions': positions,
            'count': len(positions),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/performance')
def get_performance():
    """
    Get performance metrics and history
    
    Returns:
        JSON with performance data
    """
    try:
        coordinator = DASHBOARD_STATE.get('coordinator')
        
        if coordinator is None:
            return jsonify({'error': 'Trading coordinator not initialized'})
        
        # Calculate performance metrics
        metrics = coordinator.metrics
        closed_trades = coordinator.closed_trades
        
        # Calculate daily P&L
        daily_pnl = {}
        for trade in closed_trades:
            exit_date = trade['exit_date'][:10]  # Get date only
            if exit_date not in daily_pnl:
                daily_pnl[exit_date] = 0
            daily_pnl[exit_date] += trade['pnl']
        
        # Calculate cumulative returns
        cumulative_returns = []
        cumulative_pnl = 0
        for date in sorted(daily_pnl.keys()):
            cumulative_pnl += daily_pnl[date]
            cumulative_returns.append({
                'date': date,
                'pnl': cumulative_pnl,
                'return_pct': (cumulative_pnl / coordinator.initial_capital) * 100
            })
        
        # Win/loss distribution
        win_sizes = [t['pnl_pct'] for t in closed_trades if t['pnl'] > 0]
        loss_sizes = [t['pnl_pct'] for t in closed_trades if t['pnl'] <= 0]
        
        avg_win = sum(win_sizes) / len(win_sizes) if win_sizes else 0
        avg_loss = sum(loss_sizes) / len(loss_sizes) if loss_sizes else 0
        
        return jsonify({
            'metrics': metrics,
            'cumulative_returns': cumulative_returns,
            'daily_pnl': daily_pnl,
            'win_loss_stats': {
                'avg_win_pct': avg_win,
                'avg_loss_pct': avg_loss,
                'win_count': len(win_sizes),
                'loss_count': len(loss_sizes),
                'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trades')
def get_trades():
    """
    Get trade history
    
    Query params:
        limit: Maximum number of trades to return (default: 50)
        offset: Offset for pagination (default: 0)
    
    Returns:
        JSON with trade history
    """
    try:
        coordinator = DASHBOARD_STATE.get('coordinator')
        
        if coordinator is None:
            return jsonify({'error': 'Trading coordinator not initialized'})
        
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        all_trades = coordinator.closed_trades
        total_count = len(all_trades)
        
        # Sort by exit date descending (most recent first)
        sorted_trades = sorted(all_trades, key=lambda x: x['exit_date'], reverse=True)
        
        # Paginate
        paginated_trades = sorted_trades[offset:offset + limit]
        
        return jsonify({
            'trades': paginated_trades,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/market-context')
def get_market_context():
    """
    Get current market context and sentiment
    
    Returns:
        JSON with market sentiment and analysis
    """
    try:
        coordinator = DASHBOARD_STATE.get('coordinator')
        
        if coordinator is None:
            return jsonify({'error': 'Trading coordinator not initialized'})
        
        market_context = coordinator.get_market_context()
        
        return jsonify({
            'context': market_context,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting market context: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts')
def get_alerts():
    """
    Get recent alerts
    
    Query params:
        limit: Maximum number of alerts to return (default: 50)
    
    Returns:
        JSON with recent alerts
    """
    try:
        limit = int(request.args.get('limit', 50))
        
        alerts = DASHBOARD_STATE.get('alerts', [])
        
        # Sort by timestamp descending
        sorted_alerts = sorted(alerts, key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'alerts': sorted_alerts[:limit],
            'total_count': len(alerts),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/risk')
def get_risk_metrics():
    """
    Get risk exposure metrics
    
    Returns:
        JSON with risk metrics
    """
    try:
        coordinator = DASHBOARD_STATE.get('coordinator')
        
        if coordinator is None:
            return jsonify({'error': 'Trading coordinator not initialized'})
        
        positions = coordinator.positions
        portfolio_status = coordinator.get_portfolio_status()
        
        # Calculate portfolio heat (total risk as % of capital)
        total_risk = 0
        position_risks = []
        
        for symbol, position in positions.items():
            # Risk = (entry_price - stop_loss) * shares
            position_risk = (position.entry_price - position.stop_loss) * position.shares
            position_risk_pct = (position_risk / coordinator.initial_capital) * 100
            
            total_risk += position_risk
            
            position_risks.append({
                'symbol': symbol,
                'risk_amount': position_risk,
                'risk_pct': position_risk_pct,
                'position_size_pct': (position.shares * position.entry_price / coordinator.initial_capital) * 100
            })
        
        portfolio_heat = (total_risk / coordinator.initial_capital) * 100
        
        # Calculate concentration risk (largest position)
        max_position_size = max(
            [(p.shares * p.entry_price / coordinator.initial_capital) * 100 for p in positions.values()],
            default=0
        )
        
        return jsonify({
            'portfolio_heat': portfolio_heat,
            'max_portfolio_heat': coordinator.config['risk_management']['max_portfolio_heat'] * 100,
            'position_risks': position_risks,
            'concentration': {
                'max_position_pct': max_position_size,
                'max_allowed_pct': coordinator.config['risk_management']['max_single_trade_risk'] * 100
            },
            'drawdown': {
                'current_pct': portfolio_status['performance']['max_drawdown'],
                'peak_capital': coordinator.metrics['peak_capital'],
                'current_capital': portfolio_status['capital']['total_value']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/intraday')
def get_intraday_status():
    """
    Get intraday monitoring status
    
    Returns:
        JSON with intraday scan statistics
    """
    try:
        coordinator = DASHBOARD_STATE.get('coordinator')
        
        if coordinator is None:
            return jsonify({'error': 'Trading coordinator not initialized'})
        
        intraday_stats = coordinator.intraday_manager.get_session_stats()
        
        # Get tracked opportunities
        opportunities = coordinator.intraday_manager.get_tracked_opportunities(
            min_strength=60,
            max_count=20
        )
        
        return jsonify({
            'stats': intraday_stats,
            'opportunities': opportunities,
            'scheduler_running': coordinator.scheduler is not None,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting intraday status: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def add_alert(alert_type: str, message: str, symbol: Optional[str] = None, severity: str = 'info'):
    """
    Add an alert to the dashboard
    
    Args:
        alert_type: Type of alert (e.g., 'position_opened', 'breakout', 'risk')
        message: Alert message
        symbol: Optional stock symbol
        severity: Alert severity ('info', 'warning', 'error', 'success')
    """
    alert = {
        'timestamp': datetime.now().isoformat(),
        'type': alert_type,
        'message': message,
        'symbol': symbol,
        'severity': severity
    }
    
    DASHBOARD_STATE['alerts'].append(alert)
    
    # Keep only last 500 alerts
    if len(DASHBOARD_STATE['alerts']) > 500:
        DASHBOARD_STATE['alerts'] = DASHBOARD_STATE['alerts'][-500:]
    
    logger.info(f"Alert: [{alert_type}] {message}")


def set_coordinator(coordinator):
    """
    Set the trading coordinator instance
    
    Args:
        coordinator: LiveTradingCoordinator instance
    """
    DASHBOARD_STATE['coordinator'] = coordinator
    logger.info("Trading coordinator registered with dashboard")


def start_dashboard(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Start the dashboard server
    
    Args:
        host: Host address
        port: Port number
        debug: Enable debug mode
    """
    logger.info(f"Starting Live Trading Dashboard on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Example: Start dashboard in standalone mode
    start_dashboard(host='0.0.0.0', port=5000, debug=True)

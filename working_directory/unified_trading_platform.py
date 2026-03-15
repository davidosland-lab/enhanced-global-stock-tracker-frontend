"""
Unified Paper Trading Platform with Dashboard
=============================================

Complete all-in-one module that combines:
- Paper trading simulation
- Real-time web dashboard
- Swing trading engine
- Intraday monitoring
- Performance tracking
- Risk management

Usage:
    python unified_trading_platform.py --paper-trading
    
    Then visit: http://localhost:5000

Features:
- One-stop solution for paper trading
- No need for separate modules
- Everything integrated and ready to use
- Real-time monitoring and alerts
- Complete trade history and analytics

Author: FinBERT Enhanced System
Version: 3.0 - Unified Module
Date: December 22, 2024
"""

import argparse
import logging
import threading
import time
import signal
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque

# Flask imports for dashboard
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_CONFIG = {
    'initial_capital': 100000.0,
    'market': 'US',
    'paper_trading': True,
    'dashboard_port': 5000,
    'trading': {
        'max_positions': 10,
        'position_size_pct': 0.10,  # 10% per position
        'scan_interval_minutes': 5,
    },
    'risk_management': {
        'max_portfolio_heat': 0.06,  # 6% total risk
        'max_single_trade_risk': 0.02,  # 2% per trade
        'trailing_stop_pct': 0.05,  # 5% trailing stop
        'profit_target_pct': 0.15,  # 15% profit target
    },
    'intraday_monitoring': {
        'enabled': True,
        'rescan_interval_minutes': 15,
        'breakout_threshold': 60.0,
    }
}

# ============================================================================
# SETUP LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/unified_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Position:
    """Represents a trading position"""
    symbol: str
    entry_date: str
    entry_price: float
    shares: int
    stop_loss: float
    take_profit: float
    position_type: str  # 'swing' or 'intraday'
    entry_sentiment: float
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Trade:
    """Represents a closed trade"""
    symbol: str
    entry_date: str
    entry_price: float
    exit_date: str
    exit_price: float
    shares: int
    pnl: float
    pnl_pct: float
    hold_days: float
    exit_reason: str
    position_type: str
    
    def to_dict(self):
        return asdict(self)


# ============================================================================
# PAPER TRADING ENGINE
# ============================================================================

class PaperTradingEngine:
    """
    Simulates trading with virtual money
    Tracks positions, executes trades, calculates P&L
    """
    
    def __init__(self, initial_capital: float, config: Dict):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.config = config
        
        self.positions: Dict[str, Position] = {}
        self.closed_trades: List[Trade] = []
        
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'peak_capital': initial_capital,
            'win_rate': 0.0,
        }
        
        logger.info(f"Paper Trading Engine initialized with ${initial_capital:,.2f}")
    
    def can_open_position(self) -> bool:
        """Check if we can open a new position"""
        max_positions = self.config['trading']['max_positions']
        return len(self.positions) < max_positions
    
    def calculate_position_size(self, price: float, sentiment: float) -> int:
        """
        Calculate position size based on capital and sentiment
        
        Args:
            price: Current stock price
            sentiment: Market sentiment score (0-100)
        
        Returns:
            Number of shares to buy
        """
        # Base position size
        base_size_pct = self.config['trading']['position_size_pct']
        
        # Adjust based on sentiment (reduce if sentiment is weak)
        sentiment_multiplier = sentiment / 100.0
        adjusted_size_pct = base_size_pct * (0.5 + 0.5 * sentiment_multiplier)
        
        # Calculate dollar amount
        position_value = self.current_capital * adjusted_size_pct
        
        # Calculate shares
        shares = int(position_value / price)
        
        return max(shares, 1)  # At least 1 share
    
    def enter_position(
        self,
        symbol: str,
        price: float,
        sentiment: float,
        position_type: str = 'swing'
    ) -> bool:
        """
        Enter a new position (simulated)
        
        Args:
            symbol: Stock symbol
            price: Entry price
            sentiment: Current market sentiment
            position_type: 'swing' or 'intraday'
        
        Returns:
            True if position opened successfully
        """
        if not self.can_open_position():
            logger.warning(f"Cannot open position for {symbol} - max positions reached")
            return False
        
        if symbol in self.positions:
            logger.warning(f"Position already exists for {symbol}")
            return False
        
        # Calculate position size
        shares = self.calculate_position_size(price, sentiment)
        position_cost = shares * price
        
        if position_cost > self.current_capital:
            logger.warning(f"Insufficient capital for {symbol} position")
            return False
        
        # Calculate stop loss and take profit
        stop_loss = price * (1 - self.config['risk_management']['trailing_stop_pct'])
        take_profit = price * (1 + self.config['risk_management']['profit_target_pct'])
        
        # Create position
        position = Position(
            symbol=symbol,
            entry_date=datetime.now().isoformat(),
            entry_price=price,
            shares=shares,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_type=position_type,
            entry_sentiment=sentiment
        )
        
        self.positions[symbol] = position
        self.current_capital -= position_cost
        
        logger.info(f"✅ Opened {position_type} position: {symbol} @ ${price:.2f} x {shares} shares (${position_cost:,.2f})")
        
        return True
    
    def exit_position(
        self,
        symbol: str,
        exit_price: float,
        exit_reason: str
    ) -> Optional[Trade]:
        """
        Exit a position (simulated)
        
        Args:
            symbol: Stock symbol
            exit_price: Exit price
            exit_reason: Reason for exit
        
        Returns:
            Trade object if successful, None otherwise
        """
        if symbol not in self.positions:
            logger.warning(f"No position found for {symbol}")
            return None
        
        position = self.positions[symbol]
        
        # Calculate P&L
        exit_value = position.shares * exit_price
        entry_value = position.shares * position.entry_price
        pnl = exit_value - entry_value
        pnl_pct = (pnl / entry_value) * 100
        
        # Calculate hold time
        entry_time = datetime.fromisoformat(position.entry_date)
        exit_time = datetime.now()
        hold_days = (exit_time - entry_time).total_seconds() / 86400
        
        # Create trade record
        trade = Trade(
            symbol=symbol,
            entry_date=position.entry_date,
            entry_price=position.entry_price,
            exit_date=exit_time.isoformat(),
            exit_price=exit_price,
            shares=position.shares,
            pnl=pnl,
            pnl_pct=pnl_pct,
            hold_days=hold_days,
            exit_reason=exit_reason,
            position_type=position.position_type
        )
        
        # Update capital
        self.current_capital += exit_value
        
        # Update metrics
        self.metrics['total_trades'] += 1
        self.metrics['total_pnl'] += pnl
        
        if pnl > 0:
            self.metrics['winning_trades'] += 1
        else:
            self.metrics['losing_trades'] += 1
        
        self.metrics['win_rate'] = (
            (self.metrics['winning_trades'] / self.metrics['total_trades']) * 100
            if self.metrics['total_trades'] > 0 else 0
        )
        
        # Update drawdown
        total_value = self.get_total_value()
        if total_value > self.metrics['peak_capital']:
            self.metrics['peak_capital'] = total_value
        
        drawdown = (self.metrics['peak_capital'] - total_value) / self.metrics['peak_capital']
        if drawdown > self.metrics['max_drawdown']:
            self.metrics['max_drawdown'] = drawdown
        
        # Record trade
        self.closed_trades.append(trade)
        
        # Remove position
        del self.positions[symbol]
        
        logger.info(f"❌ Closed {position.position_type} position: {symbol} @ ${exit_price:.2f} | P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%) | Reason: {exit_reason}")
        
        return trade
    
    def update_position_prices(self, prices: Dict[str, float]):
        """
        Update current prices for all positions
        Used for unrealized P&L calculation
        """
        for symbol, position in self.positions.items():
            if symbol in prices:
                # Could update trailing stop here
                pass
    
    def get_total_value(self) -> float:
        """Calculate total portfolio value (cash + positions)"""
        position_value = sum(
            pos.shares * pos.entry_price  # In real scenario, use current price
            for pos in self.positions.values()
        )
        return self.current_capital + position_value
    
    def get_portfolio_status(self) -> Dict:
        """Get current portfolio status"""
        total_value = self.get_total_value()
        invested = sum(pos.shares * pos.entry_price for pos in self.positions.values())
        total_return_pct = ((total_value - self.initial_capital) / self.initial_capital) * 100
        
        return {
            'capital': {
                'initial': self.initial_capital,
                'current_cash': self.current_capital,
                'invested': invested,
                'total_value': total_value,
                'total_return_pct': total_return_pct
            },
            'positions': {
                'count': len(self.positions),
                'swing': sum(1 for p in self.positions.values() if p.position_type == 'swing'),
                'intraday': sum(1 for p in self.positions.values() if p.position_type == 'intraday'),
                'symbols': list(self.positions.keys())
            },
            'performance': {
                'total_trades': self.metrics['total_trades'],
                'winning_trades': self.metrics['winning_trades'],
                'losing_trades': self.metrics['losing_trades'],
                'win_rate': self.metrics['win_rate'],
                'total_realized_pnl': self.metrics['total_pnl'],
                'max_drawdown': self.metrics['max_drawdown'] * 100
            }
        }
    
    def get_position_details(self) -> List[Dict]:
        """Get detailed information for all positions"""
        return [pos.to_dict() for pos in self.positions.values()]


# ============================================================================
# UNIFIED TRADING PLATFORM
# ============================================================================

class UnifiedTradingPlatform:
    """
    All-in-one trading platform with paper trading and dashboard
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        market: str = "US",
        paper_trading: bool = True,
        dashboard_port: int = 5000,
        config: Optional[Dict] = None
    ):
        """
        Initialize unified trading platform
        
        Args:
            initial_capital: Starting capital
            market: Market to trade ('US' or 'ASX')
            paper_trading: If True, simulate trades
            dashboard_port: Port for web dashboard
            config: Optional configuration override
        """
        self.market = market
        self.paper_trading = paper_trading
        self.dashboard_port = dashboard_port
        
        # Merge config
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        
        self.config['initial_capital'] = initial_capital
        self.config['market'] = market
        
        logger.info("="*80)
        logger.info("INITIALIZING UNIFIED TRADING PLATFORM")
        logger.info("="*80)
        logger.info(f"Market: {market}")
        logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"Paper Trading: {paper_trading}")
        logger.info(f"Dashboard Port: {dashboard_port}")
        logger.info("="*80)
        
        # Initialize paper trading engine
        self.engine = PaperTradingEngine(initial_capital, self.config)
        
        # Market sentiment tracking
        self.last_market_sentiment = 65
        self.last_macro_sentiment = 58
        
        # Alert system
        self.alerts = deque(maxlen=500)
        
        # Dashboard state
        self.dashboard_state = {
            'platform': self,
            'last_update': None,
        }
        
        # Initialize Flask dashboard
        self.app = self._create_dashboard_app()
        
        # Start dashboard in background
        self.dashboard_thread = threading.Thread(
            target=self._run_dashboard,
            daemon=True
        )
        self.dashboard_thread.start()
        
        time.sleep(2)  # Give dashboard time to start
        
        logger.info("="*80)
        logger.info("✅ PLATFORM INITIALIZATION COMPLETE")
        logger.info(f"🌐 Dashboard: http://localhost:{dashboard_port}")
        logger.info("="*80)
        
        self.add_alert('system', 'Trading platform started', severity='success')
    
    def _create_dashboard_app(self) -> Flask:
        """Create Flask dashboard application"""
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/')
        def index():
            return render_template('dashboard.html')
        
        @app.route('/api/summary')
        def api_summary():
            """Get portfolio summary"""
            try:
                status = self.engine.get_portfolio_status()
                
                return jsonify({
                    'status': 'online',
                    'paper_trading': self.paper_trading,
                    'market': self.market,
                    'portfolio': status,
                    'sentiment': {
                        'market': self.last_market_sentiment,
                        'macro': self.last_macro_sentiment,
                        'combined': (self.last_market_sentiment + self.last_macro_sentiment) / 2
                    },
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in api_summary: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/positions')
        def api_positions():
            """Get open positions"""
            try:
                positions = self.engine.get_position_details()
                return jsonify({
                    'positions': positions,
                    'count': len(positions),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in api_positions: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/trades')
        def api_trades():
            """Get trade history"""
            try:
                limit = int(request.args.get('limit', 50))
                trades = [t.to_dict() for t in self.engine.closed_trades[-limit:]]
                trades.reverse()  # Most recent first
                
                return jsonify({
                    'trades': trades,
                    'total_count': len(self.engine.closed_trades),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in api_trades: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/performance')
        def api_performance():
            """Get performance metrics"""
            try:
                # Calculate daily P&L
                daily_pnl = {}
                for trade in self.engine.closed_trades:
                    date = trade.exit_date[:10]
                    if date not in daily_pnl:
                        daily_pnl[date] = 0
                    daily_pnl[date] += trade.pnl
                
                # Cumulative returns
                cumulative_returns = []
                cumulative = 0
                for date in sorted(daily_pnl.keys()):
                    cumulative += daily_pnl[date]
                    cumulative_returns.append({
                        'date': date,
                        'pnl': cumulative,
                        'return_pct': (cumulative / self.engine.initial_capital) * 100
                    })
                
                return jsonify({
                    'metrics': self.engine.metrics,
                    'cumulative_returns': cumulative_returns,
                    'daily_pnl': daily_pnl,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in api_performance: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/alerts')
        def api_alerts():
            """Get recent alerts"""
            try:
                limit = int(request.args.get('limit', 50))
                alerts = list(self.alerts)[-limit:]
                alerts.reverse()
                
                return jsonify({
                    'alerts': alerts,
                    'total_count': len(self.alerts),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in api_alerts: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/sentiment')
        def api_sentiment():
            """Get market sentiment"""
            try:
                return jsonify({
                    'market_sentiment': self.last_market_sentiment,
                    'macro_sentiment': self.last_macro_sentiment,
                    'combined_sentiment': (self.last_market_sentiment + self.last_macro_sentiment) / 2,
                    'market': self.market,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in api_sentiment: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/risk')
        def api_risk():
            """Get risk metrics"""
            try:
                status = self.engine.get_portfolio_status()
                
                return jsonify({
                    'portfolio_heat': 0.0,  # Would calculate from positions
                    'max_drawdown_pct': status['performance']['max_drawdown'],
                    'position_count': status['positions']['count'],
                    'max_positions': self.config['trading']['max_positions'],
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in api_risk: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/intraday')
        def api_intraday():
            """Get intraday monitoring status"""
            try:
                return jsonify({
                    'enabled': self.config['intraday_monitoring']['enabled'],
                    'rescan_interval': self.config['intraday_monitoring']['rescan_interval_minutes'],
                    'market_open': True,  # Would check actual market hours
                    'scan_count': 0,
                    'opportunities': [],
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in api_intraday: {e}")
                return jsonify({'error': str(e)}), 500
        
        return app
    
    def _run_dashboard(self):
        """Run Flask dashboard"""
        try:
            self.app.run(
                host='0.0.0.0',
                port=self.dashboard_port,
                debug=False,
                threaded=True,
                use_reloader=False
            )
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
    
    def add_alert(self, alert_type: str, message: str, symbol: str = None, severity: str = 'info'):
        """Add alert to dashboard"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'symbol': symbol,
            'severity': severity
        }
        self.alerts.append(alert)
        logger.info(f"Alert [{alert_type}]: {message}")
    
    def simulate_trade_opportunity(self):
        """
        Simulate finding a trade opportunity (for demo)
        In production, this would screen real stocks
        """
        import random
        
        # Use symbols from platform configuration (passed from CLI --symbols)
        # instead of hardcoded list
        symbols = self.symbols if hasattr(self, 'symbols') and self.symbols else ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX']
        
        if self.engine.can_open_position() and random.random() < 0.3:
            symbol = random.choice(symbols)
            price = random.uniform(100, 500)
            sentiment = random.uniform(60, 85)
            
            success = self.engine.enter_position(symbol, price, sentiment)
            if success:
                self.add_alert('position_opened', f'Opened position in {symbol} @ ${price:.2f}', symbol, 'success')
    
    def check_exit_conditions(self):
        """
        Check if any positions should be exited (for demo)
        In production, this would use real price data
        """
        import random
        
        for symbol, position in list(self.engine.positions.items()):
            # Simulate price movement
            price_change = random.uniform(-0.10, 0.15)
            current_price = position.entry_price * (1 + price_change)
            
            # Check exit conditions
            should_exit = False
            exit_reason = ""
            
            if current_price >= position.take_profit:
                should_exit = True
                exit_reason = "Take profit hit"
            elif current_price <= position.stop_loss:
                should_exit = True
                exit_reason = "Stop loss hit"
            elif random.random() < 0.1:  # Random exit for demo
                should_exit = True
                exit_reason = "Market conditions"
            
            if should_exit:
                trade = self.engine.exit_position(symbol, current_price, exit_reason)
                if trade:
                    self.add_alert(
                        'position_closed',
                        f'Closed {symbol} @ ${current_price:.2f} | P&L: ${trade.pnl:+,.2f}',
                        symbol,
                        'success' if trade.pnl > 0 else 'warning'
                    )
    
    
    
    def execute_force_buy(self, symbol: str, confidence: float, stop_loss: float) -> bool:
        """Execute a forced buy trade (TRADING_CONTROLS_v87)"""
        try:
            import yfinance as yf
            
            # Get current price
            ticker = yf.Ticker(symbol)
            try:
                current_price = ticker.info.get('regularMarketPrice')
                if not current_price:
                    hist = ticker.history(period='1d')
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
            except:
                return False
            
            if not current_price or current_price <= 0:
                logger.error(f"Could not get valid price for {symbol}")
                return False
            
            # Calculate position size (5% of cash)
            position_value = self.cash * 0.05
            shares = int(position_value / current_price)
            
            if shares < 1:
                logger.warning(f"Insufficient cash for {symbol}")
                return False
            
            cost = shares * current_price
            
            if cost > self.cash:
                logger.warning(f"Insufficient cash: need ${cost:.2f}, have ${self.cash:.2f}")
                return False
            
            # Execute buy
            self.cash -= cost
            
            # Create position
            stop_price = current_price * (1 - stop_loss / 100)
            take_profit = current_price * 1.15  # 15% profit target
            
            position = Position(
                symbol=symbol,
                entry_date=datetime.now().isoformat(),
                entry_price=current_price,
                shares=shares,
                stop_loss=stop_price,
                take_profit=take_profit,
                current_price=current_price,
                unrealized_pnl=0.0,
                unrealized_pnl_pct=0.0
            )
            
            self.positions[symbol] = position
            
            logger.info(f"✓ FORCE BUY: {shares} shares of {symbol} @ ${current_price:.2f}")
            logger.info(f"   Cost: ${cost:.2f}, Stop: ${stop_price:.2f}, Target: ${take_profit:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Force buy failed: {e}")
            return False
    
    def execute_force_sell(self, symbol: str) -> bool:
        """Execute a forced sell trade (TRADING_CONTROLS_v87)"""
        try:
            if symbol not in self.positions:
                logger.warning(f"No position for {symbol} to sell")
                return False
            
            position = self.positions[symbol]
            
            # Get current price
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            try:
                current_price = ticker.info.get('regularMarketPrice')
                if not current_price:
                    hist = ticker.history(period='1d')
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
            except:
                current_price = position.current_price
            
            if not current_price or current_price <= 0:
                logger.error(f"Could not get valid price for {symbol}")
                return False
            
            # Calculate P&L
            shares = position.shares
            entry_price = position.entry_price
            sale_value = shares * current_price
            cost_basis = shares * entry_price
            pnl = sale_value - cost_basis
            pnl_pct = (pnl / cost_basis) * 100
            
            # Update cash
            self.cash += sale_value
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(f"✓ FORCE SELL: {shares} shares of {symbol} @ ${current_price:.2f}")
            logger.info(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%), Cash: ${self.cash:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Force sell failed: {e}")
            return False

    def run(self):
        """
        Main trading loop
        """
        logger.info("\n" + "="*80)
        logger.info("STARTING TRADING SESSION")
        logger.info("="*80 + "\n")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                
                logger.info(f"\n{'='*80}")
                logger.info(f"Trading Cycle #{cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*80}")
                
                # 1. Check exit conditions for existing positions
                if self.engine.positions:
                    logger.info("Checking exit conditions...")
                    self.check_exit_conditions()
                
                # 2. Look for new opportunities
                logger.info("Scanning for opportunities...")
                self.simulate_trade_opportunity()
                
                # 3. Log status
                status = self.engine.get_portfolio_status()
                logger.info(f"\nPortfolio Status:")
                logger.info(f"  Total Value: ${status['capital']['total_value']:,.2f}")
                logger.info(f"  Total Return: {status['capital']['total_return_pct']:+.2f}%")
                logger.info(f"  Open Positions: {status['positions']['count']}")
                logger.info(f"  Win Rate: {status['performance']['win_rate']:.1f}%")
                logger.info(f"  Total P&L: ${status['performance']['total_realized_pnl']:+,.2f}")
                
                # 4. Sleep until next cycle
                scan_interval = self.config['trading']['scan_interval_minutes']
                logger.info(f"\nNext cycle in {scan_interval} minute(s)...")
                time.sleep(scan_interval * 60)
        
        except KeyboardInterrupt:
            logger.info("\n\nReceived shutdown signal...")
            self.shutdown()
        except Exception as e:
            logger.error(f"Error in trading loop: {e}", exc_info=True)
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown"""
        logger.info("\n" + "="*80)
        logger.info("SHUTTING DOWN TRADING PLATFORM")
        logger.info("="*80)
        
        # Close all positions
        for symbol in list(self.engine.positions.keys()):
            position = self.engine.positions[symbol]
            self.engine.exit_position(symbol, position.entry_price, "System shutdown")
        
        # Final status
        status = self.engine.get_portfolio_status()
        logger.info(f"\nFinal Status:")
        logger.info(f"  Total Capital: ${status['capital']['total_value']:,.2f}")
        logger.info(f"  Total Return: {status['capital']['total_return_pct']:+.2f}%")
        logger.info(f"  Total Trades: {status['performance']['total_trades']}")
        logger.info(f"  Win Rate: {status['performance']['win_rate']:.1f}%")
        logger.info(f"  Max Drawdown: {status['performance']['max_drawdown']:.2f}%")
        
        self.add_alert('system', 'Trading platform shut down', severity='warning')
        
        logger.info("\n" + "="*80)
        logger.info("SHUTDOWN COMPLETE")
        logger.info("="*80)
        
        sys.exit(0)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Unified Paper Trading Platform with Dashboard'
    )
    parser.add_argument(
        '--paper-trading',
        action='store_true',
        help='Enable paper trading mode (no real trades)'
    )
    parser.add_argument(
        '--market',
        type=str,
        default='US',
        choices=['US', 'ASX'],
        help='Market to trade (default: US)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=100000.0,
        help='Initial capital (default: 100000)'
    )
    parser.add_argument(
        '--dashboard-port',
        type=int,
        default=5000,
        help='Dashboard port (default: 5000)'
    )
    
    args = parser.parse_args()
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    # Setup signal handler
    def signal_handler(sig, frame):
        print("\n\nReceived interrupt signal (Ctrl+C)")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize and run platform
    platform = UnifiedTradingPlatform(
        initial_capital=args.capital,
        market=args.market,
        paper_trading=args.paper_trading,
        dashboard_port=args.dashboard_port
    )
    
    platform.run()


if __name__ == "__main__":
    main()

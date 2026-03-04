"""
Manual Paper Trading Platform - Phase 3 Enhanced
================================================

Integrates manual trading with Phase 3 swing trading enhancements and intraday monitoring.

Features:
- Manual control over all trades
- Phase 3 swing trading enhancements (regime detection, multi-timeframe, volatility sizing)
- Intraday monitoring and alerts
- Cross-timeframe decision making
- Real-time market sentiment
- Advanced risk management

Usage:
    python manual_trading_phase3.py --port 5004
    
Commands:
    buy('AAPL', 100)      # Buy with Phase 3 enhancements
    sell('AAPL')          # Sell with cross-timeframe analysis
    status()              # Portfolio with swing/intraday breakdown
    positions()           # Positions with regime and sentiment
    scan_intraday()       # Manual intraday scan
    market_sentiment()    # Current market conditions
"""

import argparse
import yfinance as yf
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Import from unified platform
from unified_trading_platform import UnifiedTradingPlatform, Position, Trade

# Import Phase 3 signal generator
from phase3_signal_generator import Phase3SignalGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ManualTradingPhase3(UnifiedTradingPlatform):
    """
    Manual trading platform with Phase 3 enhancements
    """
    
    def __init__(self, initial_capital=100000, dashboard_port=5000, config_file=None):
        """
        Initialize Phase 3 enhanced manual trading platform
        
        Args:
            initial_capital: Starting capital
            dashboard_port: Dashboard port (default: 5000, recommended: 5004)
            config_file: Path to Phase 3 configuration JSON
        """
        super().__init__(
            initial_capital=initial_capital,
            paper_trading=True,
            dashboard_port=dashboard_port
        )
        
        # Load Phase 3 configuration
        self.phase3_config = self._load_phase3_config(config_file)
        
        # Phase 3 state
        self.current_regime = "neutral"  # bullish, neutral, bearish
        self.market_sentiment = 50.0     # 0-100
        self.intraday_alerts = []
        self.last_intraday_scan = None
        
        # Enhanced tracking
        self.position_regimes = {}  # Track regime per position
        self.position_signals = {}  # Track entry signals
        
        # Initialize Phase 3 signal generator with ML
        self.signal_generator = Phase3SignalGenerator(self.phase3_config, use_ml=True)
        
        # Watchlist for recommendations
        self.watchlist = []
        
        print("\n" + "="*80)
        print("MANUAL PAPER TRADING PLATFORM - PHASE 3 ENHANCED")
        print("="*80)
        print("\nPhase 3 Features Enabled:")
        print(f"  ✓ Regime Detection: {self.phase3_config['swing_trading'].get('use_regime_detection', True)}")
        print(f"  ✓ Multi-Timeframe Analysis: {self.phase3_config['swing_trading'].get('use_multi_timeframe', True)}")
        print(f"  ✓ Volatility Sizing: {self.phase3_config['swing_trading'].get('use_volatility_sizing', True)}")
        print(f"  ✓ Trailing Stops: {self.phase3_config['swing_trading'].get('use_trailing_stop', True)}")
        print(f"  ✓ Intraday Monitoring: {self.phase3_config['intraday_monitoring'].get('scan_interval_minutes', 15)} min intervals")
        print(f"  ✓ Cross-Timeframe Integration: Entry & Exit Enhancement")
        print("\nCommands:")
        print("  buy('SYMBOL', quantity)           - Buy with Phase 3 analysis")
        print("  sell('SYMBOL')                    - Sell with cross-timeframe checks")
        print("  status()                          - Portfolio status")
        print("  positions()                       - Open positions with regime")
        print("  scan_intraday()                   - Manual intraday scan")
        print("  market_sentiment()                - Current market conditions")
        print("  update_regime('SYMBOL', 'bullish') - Manually set regime")
        print(f"\nDashboard: http://localhost:{dashboard_port}")
        print("="*80 + "\n")
    
    def _load_phase3_config(self, config_file: Optional[str]) -> Dict:
        """Load Phase 3 configuration"""
        # Try provided config file
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading config {config_file}: {e}")
        
        # Try default location
        default_path = Path("swing_intraday_integration_v1.0/config.json")
        if default_path.exists():
            try:
                with open(default_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading default config: {e}")
        
        # Return default config
        return self._get_default_phase3_config()
    
    def _get_default_phase3_config(self) -> Dict:
        """Get default Phase 3 configuration"""
        return {
            'swing_trading': {
                'holding_period_days': 5,
                'stop_loss_percent': 3.0,
                'confidence_threshold': 52.0,
                'max_position_size': 0.25,
                'use_trailing_stop': True,
                'use_profit_targets': True,
                'use_regime_detection': True,
                'use_multi_timeframe': True,
                'use_volatility_sizing': True,
                'quick_profit_target_pct': 12.0,
                'profit_target_pct': 8.0
            },
            'intraday_monitoring': {
                'scan_interval_minutes': 15,
                'breakout_threshold': 70.0,
                'price_change_threshold': 2.0,
                'volume_multiplier': 1.5,
                'min_signal_strength': 60.0
            },
            'risk_management': {
                'max_total_positions': 3,
                'max_portfolio_heat': 0.06,
                'max_single_trade_risk': 0.02,
                'use_position_scaling': True
            },
            'cross_timeframe': {
                'use_intraday_for_entries': True,
                'use_intraday_for_exits': True,
                'sentiment_boost_threshold': 70,
                'sentiment_block_threshold': 30,
                'early_exit_threshold': 80,
                'position_size_boost_pct': 0.05
            }
        }
    
    def buy(self, symbol: str, quantity: int, price: float = None, regime: str = None):
        """
        Buy shares with Phase 3 enhancements
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares
            price: Price (if None, fetches current price)
            regime: Market regime (bullish/neutral/bearish, auto-detected if None)
        """
        try:
            # Get current price if not provided
            if price is None:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                if price == 0:
                    print(f"[ERROR] Could not fetch price for {symbol}")
                    return False
            
            # Detect market regime if not provided
            if regime is None:
                regime = self._detect_regime(symbol)
            
            # Get market sentiment
            sentiment = self._get_market_sentiment(symbol)
            
            # Apply cross-timeframe analysis
            cross_analysis = self._cross_timeframe_entry_analysis(symbol, price, sentiment)
            
            # Check if entry is blocked by cross-timeframe
            if not cross_analysis['entry_allowed']:
                print(f"[BLOCKED] Entry blocked by cross-timeframe analysis")
                print(f"  Reason: {cross_analysis['block_reason']}")
                print(f"  Market Sentiment: {sentiment:.1f}/100")
                return False
            
            # Apply position size boost if applicable
            if cross_analysis['apply_boost']:
                boost_pct = self.phase3_config['cross_timeframe']['position_size_boost_pct']
                original_qty = quantity
                quantity = int(quantity * (1 + boost_pct))
                print(f"[BOOST] Position size increased: {original_qty} -> {quantity} shares")
                print(f"  Reason: Strong intraday sentiment ({sentiment:.1f}/100)")
            
            # Calculate cost
            total_cost = price * quantity
            
            if total_cost > self.engine.current_capital:
                print(f"[ERROR] Insufficient capital!")
                print(f"  Need: ${total_cost:,.2f}")
                print(f"  Have: ${self.engine.current_capital:,.2f}")
                return False
            
            # Calculate stop loss with volatility adjustment
            stop_loss_pct = self.phase3_config['swing_trading']['stop_loss_percent'] / 100
            if self.phase3_config['swing_trading'].get('use_volatility_sizing', False):
                # Adjust stop loss based on volatility (simplified)
                volatility_factor = self._estimate_volatility(symbol)
                stop_loss_pct *= volatility_factor
            
            stop_loss = price * (1 - stop_loss_pct)
            
            # Calculate profit target
            profit_target_pct = self.phase3_config['swing_trading']['profit_target_pct'] / 100
            take_profit = price * (1 + profit_target_pct)
            
            # Create position
            position = Position(
                symbol=symbol,
                entry_date=datetime.now().isoformat(),
                entry_price=price,
                shares=quantity,
                stop_loss=stop_loss,
                take_profit=take_profit,
                position_type='swing',  # Manual trades classified as swing
                entry_sentiment=sentiment
            )
            
            # Add to positions
            self.engine.positions[symbol] = position
            self.engine.current_capital -= total_cost
            
            # Track regime and signals
            self.position_regimes[symbol] = regime
            self.position_signals[symbol] = {
                'entry_date': datetime.now(),
                'entry_sentiment': sentiment,
                'regime': regime,
                'cross_timeframe_boost': cross_analysis['apply_boost']
            }
            
            # Print confirmation
            print(f"[SUCCESS] Bought {quantity} shares of {symbol} @ ${price:.2f}")
            print(f"  Total cost: ${total_cost:,.2f}")
            print(f"  Remaining cash: ${self.engine.current_capital:,.2f}")
            print(f"  Stop Loss: ${stop_loss:.2f} (-{stop_loss_pct*100:.1f}%)")
            print(f"  Take Profit: ${take_profit:.2f} (+{profit_target_pct*100:.1f}%)")
            print(f"  Market Regime: {regime.upper()}")
            print(f"  Entry Sentiment: {sentiment:.1f}/100")
            
            self.add_alert(
                'position_opened',
                f'Manual entry: {symbol} @ ${price:.2f} x {quantity} | Regime: {regime} | Sentiment: {sentiment:.1f}',
                symbol,
                'success'
            )
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error buying {symbol}: {e}")
            logger.error(f"Buy error: {e}", exc_info=True)
            return False
    
    def sell(self, symbol: str, price: float = None):
        """
        Sell shares with Phase 3 cross-timeframe analysis
        
        Args:
            symbol: Stock symbol
            price: Exit price (if None, fetches current price)
        """
        try:
            if symbol not in self.engine.positions:
                print(f"[ERROR] No position found for {symbol}")
                return False
            
            position = self.engine.positions[symbol]
            
            # Get current price if not provided
            if price is None:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                if price == 0:
                    print(f"[ERROR] Could not fetch price for {symbol}")
                    return False
            
            # Get current sentiment
            sentiment = self._get_market_sentiment(symbol)
            
            # Apply cross-timeframe exit analysis
            exit_analysis = self._cross_timeframe_exit_analysis(symbol, price, sentiment, position)
            
            # Show analysis
            print(f"\n[ANALYSIS] Cross-Timeframe Exit Analysis for {symbol}")
            print(f"  Current Price: ${price:.2f}")
            print(f"  Entry Price: ${position.entry_price:.2f}")
            print(f"  Unrealized P&L: ${(price - position.entry_price) * position.shares:+,.2f}")
            print(f"  Market Sentiment: {sentiment:.1f}/100")
            print(f"  Exit Recommendation: {exit_analysis['recommendation'].upper()}")
            print(f"  Reason: {exit_analysis['reason']}")
            
            # Exit position
            trade = self.engine.exit_position(symbol, price, exit_analysis['reason'])
            
            if trade:
                # Get entry info
                entry_info = self.position_signals.get(symbol, {})
                regime = self.position_regimes.get(symbol, 'unknown')
                
                print(f"\n[SUCCESS] Sold {trade.shares} shares of {symbol} @ ${price:.2f}")
                print(f"  P&L: ${trade.pnl:+,.2f} ({trade.pnl_pct:+.2f}%)")
                print(f"  Hold Duration: {trade.hold_duration_days:.1f} days")
                print(f"  Entry Regime: {regime.upper()}")
                print(f"  Entry Sentiment: {entry_info.get('entry_sentiment', 0):.1f}/100")
                print(f"  Exit Sentiment: {sentiment:.1f}/100")
                print(f"  New cash balance: ${self.engine.current_capital:,.2f}")
                
                self.add_alert(
                    'position_closed',
                    f'Manual exit: {symbol} | P&L: ${trade.pnl:+,.2f} ({trade.pnl_pct:+.2f}%) | {exit_analysis["reason"]}',
                    symbol,
                    'success' if trade.pnl > 0 else 'warning'
                )
                
                # Clean up tracking
                self.position_regimes.pop(symbol, None)
                self.position_signals.pop(symbol, None)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error selling {symbol}: {e}")
            logger.error(f"Sell error: {e}", exc_info=True)
            return False
    
    def positions(self):
        """Show open positions with Phase 3 enhancements"""
        if not self.engine.positions:
            print("\n[INFO] No open positions\n")
            return
        
        print("\n" + "="*90)
        print("OPEN POSITIONS - PHASE 3 ENHANCED")
        print("="*90)
        print(f"{'Symbol':<8} {'Shares':<7} {'Entry':<10} {'Current':<10} {'P&L':<15} {'Regime':<10} {'Sentiment'}")
        print("-"*90)
        
        for symbol, pos in self.engine.positions.items():
            try:
                # Fetch current price
                ticker = yf.Ticker(symbol)
                info = ticker.info
                current = info.get('currentPrice', info.get('regularMarketPrice', pos.entry_price))
                
                # Calculate P&L
                pnl = (current - pos.entry_price) * pos.shares
                pnl_pct = ((current - pos.entry_price) / pos.entry_price) * 100
                
                # Get regime and sentiment
                regime = self.position_regimes.get(symbol, 'unknown')
                signals = self.position_signals.get(symbol, {})
                sentiment = signals.get('entry_sentiment', 0)
                
                # Color coding for P&L
                pnl_str = f"${pnl:+,.2f} ({pnl_pct:+.1f}%)"
                
                print(f"{symbol:<8} {pos.shares:<7} ${pos.entry_price:<9.2f} ${current:<9.2f} {pnl_str:<15} {regime:<10} {sentiment:.1f}/100")
            except Exception as e:
                print(f"{symbol:<8} {pos.shares:<7} ${pos.entry_price:<9.2f} {'ERROR':<10} {'N/A':<15} {'unknown':<10} {'N/A'}")
        
        print("="*90 + "\n")
    
    def status(self):
        """Show portfolio status with Phase 3 breakdown"""
        status = self.engine.get_portfolio_status()
        
        print("\n" + "="*80)
        print("PORTFOLIO STATUS - PHASE 3 ENHANCED")
        print("="*80)
        print(f"Total Value:    ${status['capital']['total_value']:>15,.2f}")
        print(f"Cash:           ${status['capital']['current_cash']:>15,.2f}")
        print(f"Invested:       ${status['capital']['invested']:>15,.2f}")
        print(f"Total Return:   {status['capital']['total_return_pct']:>15.2f}%")
        print(f"\nOpen Positions: {status['positions']['count']:>15}")
        print(f"Total Trades:   {status['performance']['total_trades']:>15}")
        print(f"Win Rate:       {status['performance']['win_rate']:>15.1f}%")
        print(f"Total P&L:      ${status['performance']['total_realized_pnl']:>15,.2f}")
        print(f"Max Drawdown:   {status['performance']['max_drawdown']:>15.2f}%")
        print(f"\nCurrent Regime: {self.current_regime.upper():>15}")
        print(f"Market Sentiment:{self.market_sentiment:>14.1f}/100")
        print("="*80 + "\n")
    
    def scan_intraday(self):
        """Manually trigger intraday scan"""
        print("\n[SCAN] Running intraday scan...")
        print("="*80)
        
        # Get all symbols from positions and watchlist
        symbols = list(self.engine.positions.keys())
        
        if not symbols:
            print("[INFO] No positions to scan. Add symbols to positions or implement watchlist.")
            return
        
        alerts = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d", interval="5m")
                
                if hist.empty:
                    continue
                
                current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                prev_close = info.get('previousClose', current_price)
                
                # Calculate metrics
                price_change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close else 0
                volume = info.get('volume', 0)
                avg_volume = info.get('averageVolume', volume)
                volume_ratio = volume / avg_volume if avg_volume else 1.0
                
                # Check for breakout
                breakout_threshold = self.phase3_config['intraday_monitoring']['breakout_threshold']
                
                if abs(price_change_pct) >= 2.0 and volume_ratio >= 1.5:
                    alert = {
                        'symbol': symbol,
                        'type': 'breakout' if price_change_pct > 0 else 'breakdown',
                        'price_change_pct': price_change_pct,
                        'volume_ratio': volume_ratio,
                        'current_price': current_price
                    }
                    alerts.append(alert)
                    
                    print(f"[ALERT] {symbol}: {alert['type'].upper()}")
                    print(f"  Price Change: {price_change_pct:+.2f}%")
                    print(f"  Volume Ratio: {volume_ratio:.2f}x")
                    print(f"  Current Price: ${current_price:.2f}")
                    print()
                
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
        
        if not alerts:
            print("[INFO] No significant intraday alerts detected")
        else:
            self.intraday_alerts.extend(alerts)
        
        self.last_intraday_scan = datetime.now()
        print("="*80 + "\n")
    
    def market_sentiment(self):
        """Display current market sentiment and regime"""
        print("\n" + "="*80)
        print("MARKET CONDITIONS - PHASE 3")
        print("="*80)
        print(f"Current Regime:     {self.current_regime.upper()}")
        print(f"Market Sentiment:   {self.market_sentiment:.1f}/100")
        print(f"\nInterpretation:")
        
        if self.market_sentiment >= 70:
            print("  📈 VERY BULLISH - Strong uptrend, favorable for entries")
        elif self.market_sentiment >= 60:
            print("  ↗️  BULLISH - Positive momentum")
        elif self.market_sentiment >= 40:
            print("  ➡️  NEUTRAL - Mixed signals, proceed with caution")
        elif self.market_sentiment >= 30:
            print("  ↘️  BEARISH - Negative momentum")
        else:
            print("  📉 VERY BEARISH - Strong downtrend, consider exits")
        
        print(f"\nPhase 3 Configuration:")
        print(f"  Entry Boost Threshold:  {self.phase3_config['cross_timeframe']['sentiment_boost_threshold']}")
        print(f"  Entry Block Threshold:  {self.phase3_config['cross_timeframe']['sentiment_block_threshold']}")
        print(f"  Early Exit Threshold:   {self.phase3_config['cross_timeframe']['early_exit_threshold']}")
        print("="*80 + "\n")
    
    def update_regime(self, symbol: str, regime: str):
        """Manually update regime for a symbol"""
        valid_regimes = ['bullish', 'neutral', 'bearish']
        if regime.lower() not in valid_regimes:
            print(f"[ERROR] Invalid regime. Choose from: {', '.join(valid_regimes)}")
            return False
        
        self.position_regimes[symbol] = regime.lower()
        print(f"[SUCCESS] Updated regime for {symbol} to {regime.upper()}")
        return True
    
    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================
    
    def _detect_regime(self, symbol: str) -> str:
        """Detect market regime for symbol (simplified)"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if len(hist) < 10:
                return "neutral"
            
            # Simple moving average crossover
            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            current_price = hist['Close'].iloc[-1]
            
            if current_price > sma_20 * 1.02:
                return "bullish"
            elif current_price < sma_20 * 0.98:
                return "bearish"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Error detecting regime for {symbol}: {e}")
            return "neutral"
    
    def _get_market_sentiment(self, symbol: str) -> float:
        """Get market sentiment score (0-100)"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Simple sentiment based on price action
            current = info.get('currentPrice', 0)
            prev_close = info.get('previousClose', current)
            
            if prev_close:
                change_pct = ((current - prev_close) / prev_close) * 100
                # Map -5% to +5% change to 0-100 sentiment
                sentiment = 50 + (change_pct * 10)
                sentiment = max(0, min(100, sentiment))
                self.market_sentiment = sentiment
                return sentiment
            
            return 50.0
            
        except Exception as e:
            logger.error(f"Error getting sentiment for {symbol}: {e}")
            return 50.0
    
    def _cross_timeframe_entry_analysis(self, symbol: str, price: float, sentiment: float) -> Dict:
        """Analyze entry using cross-timeframe logic"""
        config = self.phase3_config['cross_timeframe']
        
        # Check if sentiment blocks entry
        if sentiment < config['sentiment_block_threshold']:
            return {
                'entry_allowed': False,
                'apply_boost': False,
                'block_reason': f'Market sentiment too low ({sentiment:.1f} < {config["sentiment_block_threshold"]})'
            }
        
        # Check if sentiment boosts position size
        apply_boost = sentiment >= config['sentiment_boost_threshold']
        
        return {
            'entry_allowed': True,
            'apply_boost': apply_boost,
            'block_reason': None
        }
    
    def _cross_timeframe_exit_analysis(self, symbol: str, price: float, sentiment: float, position) -> Dict:
        """Analyze exit using cross-timeframe logic"""
        config = self.phase3_config['cross_timeframe']
        
        # Calculate P&L
        pnl_pct = ((price - position.entry_price) / position.entry_price) * 100
        
        # Check for early exit signal (strong negative sentiment)
        if sentiment >= config['early_exit_threshold'] and pnl_pct > 2.0:
            return {
                'recommendation': 'exit',
                'reason': f'Strong sentiment spike ({sentiment:.1f}), take profits'
            }
        
        # Check for breakdown signal
        if sentiment < config['sentiment_block_threshold']:
            return {
                'recommendation': 'exit',
                'reason': f'Weak market sentiment ({sentiment:.1f}), reduce risk'
            }
        
        # Default to user decision
        return {
            'recommendation': 'hold',
            'reason': 'Manual exit requested'
        }
    
    def _estimate_volatility(self, symbol: str) -> float:
        """Estimate volatility factor (1.0 = normal)"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if len(hist) < 10:
                return 1.0
            
            # Calculate volatility as std dev of returns
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std()
            
            # Normalize to factor (0.5 to 2.0)
            factor = 1.0 + (volatility - 0.02) * 20  # Adjust baseline
            return max(0.5, min(2.0, factor))
            
        except Exception as e:
            logger.error(f"Error estimating volatility for {symbol}: {e}")
            return 1.0
    
    # =========================================================================
    # PHASE 3 RECOMMENDATION SYSTEM
    # =========================================================================
    
    def recommend_buy(self, symbols: List[str] = None):
        """
        Generate BUY recommendations using Phase 3 signal generation
        
        Args:
            symbols: List of symbols to analyze (uses watchlist if None)
        """
        if symbols is None:
            symbols = self.watchlist
        
        if not symbols:
            print("\n[INFO] No symbols in watchlist. Add symbols with: add_watchlist(['AAPL', 'NVDA'])")
            return
        
        print("\n" + "="*90)
        print("PHASE 3 BUY RECOMMENDATIONS - Original Backtest Methodology")
        print("="*90)
        print(f"Analyzing {len(symbols)} symbols using Phase 3 signal generation...")
        print()
        
        recommendations = []
        
        for symbol in symbols:
            try:
                # Fetch price data
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="3mo")
                
                if hist.empty or len(hist) < 50:
                    continue
                
                # Generate Phase 3 signal
                signal = self.signal_generator.generate_swing_signal(symbol, hist)
                
                if signal['recommendation'] == 'BUY':
                    current_price = hist['Close'].iloc[-1]
                    
                    # Calculate position size
                    shares = self.signal_generator.calculate_position_size(
                        symbol,
                        signal['confidence'],
                        current_price,
                        self.engine.current_capital,
                        signal['metrics']['atr_pct']
                    )
                    
                    position_value = shares * current_price
                    
                    recommendations.append({
                        'symbol': symbol,
                        'confidence': signal['confidence'],
                        'price': current_price,
                        'shares': shares,
                        'value': position_value,
                        'regime': signal['regime'],
                        'signal': signal
                    })
                    
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        if not recommendations:
            print("[INFO] No BUY signals detected at current threshold")
            print(f"     Confidence threshold: {self.phase3_config['swing_trading']['confidence_threshold']}%")
            print()
            return
        
        # Display recommendations
        print(f"{'Symbol':<8} {'Confidence':<12} {'Price':<10} {'Shares':<8} {'Value':<12} {'Regime':<10}")
        print("-"*90)
        
        for rec in recommendations:
            print(f"{rec['symbol']:<8} {rec['confidence']:>10.1f}% ${rec['price']:<9.2f} {rec['shares']:<8} ${rec['value']:<11,.0f} {rec['regime']:<10}")
        
        print("="*90)
        print(f"\nTop Recommendation: {recommendations[0]['symbol']} at {recommendations[0]['confidence']:.1f}% confidence")
        print(f"  Suggested command: buy('{recommendations[0]['symbol']}', {recommendations[0]['shares']})")
        print()
    
    def recommend_sell(self):
        """
        Generate SELL recommendations for open positions using Phase 3 exit logic
        """
        if not self.engine.positions:
            print("\n[INFO] No open positions to evaluate\n")
            return
        
        print("\n" + "="*90)
        print("PHASE 3 SELL RECOMMENDATIONS - Original Backtest Methodology")
        print("="*90)
        print(f"Evaluating {len(self.engine.positions)} open positions...")
        print()
        
        recommendations = []
        
        for symbol, position in self.engine.positions.items():
            try:
                # Fetch current data
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="3mo")
                current_price = hist['Close'].iloc[-1]
                
                # Get entry info
                entry_info = self.position_signals.get(symbol, {})
                entry_date = entry_info.get('entry_date', datetime.now())
                
                # Evaluate exit using Phase 3 methodology
                should_exit, reason = self.signal_generator.evaluate_exit(
                    symbol,
                    position.entry_price,
                    current_price,
                    entry_date,
                    hist
                )
                
                # Calculate current P&L
                pnl = (current_price - position.entry_price) * position.shares
                pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
                
                days_held = (datetime.now() - entry_date).days
                
                if should_exit:
                    recommendations.append({
                        'symbol': symbol,
                        'reason': reason,
                        'current_price': current_price,
                        'entry_price': position.entry_price,
                        'shares': position.shares,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'days_held': days_held,
                        'priority': 'HIGH' if 'Stop loss' in reason or pnl_pct < -2 else 'MEDIUM'
                    })
                else:
                    # Still show in report with HOLD status
                    print(f"[HOLD] {symbol}: {reason} | P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%) | Days: {days_held}")
                    
            except Exception as e:
                logger.error(f"Error evaluating {symbol}: {e}")
        
        print()
        
        if not recommendations:
            print("[INFO] No SELL signals detected. All positions should be held.")
            print()
            return
        
        # Sort by priority and P&L
        recommendations.sort(key=lambda x: (x['priority'], x['pnl_pct']))
        
        # Display sell recommendations
        print(f"{'Symbol':<8} {'Priority':<10} {'P&L':<15} {'Days':<6} {'Reason'}")
        print("-"*90)
        
        for rec in recommendations:
            pnl_str = f"${rec['pnl']:+,.2f} ({rec['pnl_pct']:+.1f}%)"
            print(f"{rec['symbol']:<8} {rec['priority']:<10} {pnl_str:<15} {rec['days_held']:<6} {rec['reason']}")
        
        print("="*90)
        
        if recommendations:
            top_rec = recommendations[0]
            print(f"\nTop Sell Recommendation: {top_rec['symbol']} ({top_rec['priority']} priority)")
            print(f"  Reason: {top_rec['reason']}")
            print(f"  Suggested command: sell('{top_rec['symbol']}')")
        print()
    
    def recommend_buy_ml(self, symbols: List[str] = None):
        """
        Generate ML-ENHANCED BUY recommendations using Phase 3 + ML Pipeline
        
        Combines:
        - Phase 3 technical analysis (Momentum, Trend, Volume, Volatility)
        - ML predictions (LSTM, Transformer, Ensemble, GNN)
        - Sentiment analysis (FinBERT when available, keyword-based otherwise)
        
        Args:
            symbols: List of symbols to analyze (uses watchlist if None)
        """
        if symbols is None:
            symbols = self.watchlist
        
        if not symbols:
            print("\n[INFO] No symbols in watchlist. Add symbols with: add_watchlist(['AAPL', 'NVDA'])")
            return
        
        print("\n" + "="*100)
        print("PHASE 3 + ML BUY RECOMMENDATIONS - Enhanced with Machine Learning")
        print("="*100)
        print(f"Analyzing {len(symbols)} symbols using Phase 3 + ML Pipeline...")
        print()
        
        recommendations = []
        
        # Run async signal generation
        import asyncio
        
        async def analyze_symbols():
            tasks = []
            for symbol in symbols:
                tasks.append(self._analyze_symbol_ml(symbol))
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        try:
            results = asyncio.run(analyze_symbols())
            
            for result in results:
                if isinstance(result, dict) and result.get('recommendation') == 'BUY':
                    recommendations.append(result)
        except Exception as e:
            logger.error(f"ML analysis failed: {e}")
            print("[WARNING] ML analysis failed, falling back to technical analysis")
            self.recommend_buy(symbols)
            return
        
        # Sort by combined confidence
        recommendations.sort(key=lambda x: x.get('ml_confidence', x['confidence']), reverse=True)
        
        if not recommendations:
            print("[INFO] No ML-enhanced BUY signals detected")
            print(f"     Confidence threshold: {self.phase3_config['swing_trading']['confidence_threshold']}%")
            print()
            return
        
        # Display ML-enhanced recommendations
        print(f"{'Symbol':<8} {'Tech':<8} {'ML':<8} {'Comb'd':<8} {'Price':<10} {'Shares':<8} {'Value':<12} {'Regime':<10} {'Source':<18}")
        print("-"*100)
        
        for rec in recommendations:
            print(
                f"{rec['symbol']:<8} "
                f"{rec.get('technical_confidence', rec['confidence']):>6.1f}% "
                f"{rec.get('ml_confidence', 0):>6.1f}% "
                f"{rec['confidence']:>6.1f}% "
                f"${rec['price']:<9.2f} "
                f"{rec['shares']:<8} "
                f"${rec['value']:<11,.0f} "
                f"{rec['regime']:<10} "
                f"{rec.get('ml_source', 'technical'):<18}"
            )
        
        print("="*100)
        print(f"\n🤖 Top ML-Enhanced Recommendation: {recommendations[0]['symbol']} "
              f"at {recommendations[0]['confidence']:.1f}% combined confidence")
        print(f"   Technical: {recommendations[0].get('technical_confidence', recommendations[0]['confidence']):.1f}% | "
              f"ML: {recommendations[0].get('ml_confidence', 0):.1f}%")
        print(f"   ML Source: {recommendations[0].get('ml_source', 'technical')}")
        print(f"\n   Suggested command: buy('{recommendations[0]['symbol']}', {recommendations[0]['shares']})")
        print()
    
    async def _analyze_symbol_ml(self, symbol: str):
        """Helper to analyze a single symbol with ML"""
        try:
            # Fetch price data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="3mo")
            
            if hist.empty or len(hist) < 50:
                return None
            
            # Generate ML-enhanced Phase 3 signal
            signal = await self.signal_generator.generate_ml_enhanced_signal(symbol, hist)
            
            if signal['recommendation'] == 'BUY':
                current_price = hist['Close'].iloc[-1]
                
                # Use ML position sizing if available
                if 'ml_position_size_pct' in signal:
                    shares = int((self.engine.current_capital * signal['ml_position_size_pct']) / current_price)
                else:
                    # Fallback to Phase 3 position sizing
                    shares = self.signal_generator.calculate_position_size(
                        symbol,
                        signal['confidence'],
                        current_price,
                        self.engine.current_capital,
                        signal['metrics']['atr_pct']
                    )
                
                position_value = shares * current_price
                
                return {
                    'symbol': symbol,
                    'confidence': signal['confidence'],
                    'technical_confidence': signal.get('technical_confidence', signal['confidence']),
                    'ml_confidence': signal.get('ml_confidence', 0),
                    'price': current_price,
                    'shares': shares,
                    'value': position_value,
                    'regime': signal['regime'],
                    'ml_source': signal.get('ml_source', 'technical'),
                    'ml_sentiment': signal.get('ml_sentiment', 0),
                    'recommendation': 'BUY',
                    'signal': signal
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol} with ML: {e}")
            return None
    
    def add_watchlist(self, symbols: List[str]):
        """Add symbols to watchlist for recommendations"""
        for symbol in symbols:
            symbol = symbol.upper()
            if symbol not in self.watchlist:
                self.watchlist.append(symbol)
        
        print(f"\n[SUCCESS] Watchlist updated: {', '.join(self.watchlist)}")
        print(f"  Total symbols: {len(self.watchlist)}")
        print(f"  Run recommend_buy() to get Phase 3 buy recommendations\n")
    
    def show_watchlist(self):
        """Display current watchlist"""
        if not self.watchlist:
            print("\n[INFO] Watchlist is empty")
            print("  Add symbols with: add_watchlist(['AAPL', 'NVDA', 'TSLA'])\n")
            return
        
        print("\n" + "="*60)
        print("WATCHLIST")
        print("="*60)
        print(f"Symbols: {', '.join(self.watchlist)}")
        print(f"Total: {len(self.watchlist)} symbols")
        print("="*60 + "\n")
    
    def auto_trade_recommendation(self):
        """
        Automatically execute the top Phase 3 recommendation
        
        WARNING: This executes a trade automatically based on Phase 3 signals!
        """
        print("\n[AUTO-TRADE] Analyzing watchlist for best Phase 3 opportunity...")
        
        if not self.watchlist:
            print("[ERROR] Watchlist is empty. Add symbols first.")
            return False
        
        # Generate recommendations
        recommendations = []
        
        for symbol in self.watchlist:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="3mo")
                
                if hist.empty or len(hist) < 50:
                    continue
                
                signal = self.signal_generator.generate_swing_signal(symbol, hist)
                
                if signal['recommendation'] == 'BUY':
                    current_price = hist['Close'].iloc[-1]
                    shares = self.signal_generator.calculate_position_size(
                        symbol,
                        signal['confidence'],
                        current_price,
                        self.engine.current_capital,
                        signal['metrics']['atr_pct']
                    )
                    
                    recommendations.append({
                        'symbol': symbol,
                        'confidence': signal['confidence'],
                        'price': current_price,
                        'shares': shares,
                        'signal': signal
                    })
                    
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
        
        if not recommendations:
            print("[INFO] No qualifying buy signals found")
            return False
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        top_rec = recommendations[0]
        
        print(f"\n[EXECUTING] Top Phase 3 recommendation:")
        print(f"  Symbol: {top_rec['symbol']}")
        print(f"  Confidence: {top_rec['confidence']:.1f}%")
        print(f"  Price: ${top_rec['price']:.2f}")
        print(f"  Shares: {top_rec['shares']}")
        print()
        
        # Execute the trade
        return self.buy(top_rec['symbol'], top_rec['shares'])
    
    def run(self):
        """Override auto-trading - manual mode only"""
        print("\n[READY] Manual trading mode active - Phase 3 Enhanced")
        print(f"Dashboard running at: http://localhost:{self.dashboard_port}")
        print("\nAvailable commands:")
        print("  Trading: buy(), sell(), status(), positions()")
        print("  Analysis: scan_intraday(), market_sentiment()")
        print("  Regime: update_regime('SYMBOL', 'bullish')")
        print("\n  === PHASE 3 RECOMMENDATIONS (NEW) ===")
        print("  add_watchlist(['AAPL', 'NVDA', 'TSLA'])  - Add symbols to watch")
        print("  show_watchlist()                         - Show current watchlist")
        print("  recommend_buy()                          - Get Phase 3 BUY signals")
        print("  recommend_buy_ml()                       - Get ML-ENHANCED BUY signals 🤖")
        print("  recommend_sell()                         - Get Phase 3 SELL signals")
        print("  auto_trade_recommendation()              - Auto-execute top recommendation")
        print("\nPress Ctrl+C to exit\n")
        
        try:
            import code
            code.interact(local=locals())
        except KeyboardInterrupt:
            print("\n\n[SHUTDOWN] Shutting down...")
            self.shutdown()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Manual Paper Trading Platform - Phase 3 Enhanced')
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Dashboard port (default: 5000, recommended: 5004)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=100000.0,
        help='Initial capital (default: 100000)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to Phase 3 config file (default: auto-detect)'
    )
    args = parser.parse_args()
    
    # Create platform with Phase 3 enhancements
    platform = ManualTradingPhase3(
        initial_capital=args.capital,
        dashboard_port=args.port,
        config_file=args.config
    )
    
    # Make functions available globally
    import __main__
    __main__.buy = platform.buy
    __main__.sell = platform.sell
    __main__.status = platform.status
    __main__.positions = platform.positions
    __main__.scan_intraday = platform.scan_intraday
    __main__.market_sentiment = platform.market_sentiment
    __main__.update_regime = platform.update_regime
    __main__.add_watchlist = platform.add_watchlist
    __main__.show_watchlist = platform.show_watchlist
    __main__.recommend_buy = platform.recommend_buy
    __main__.recommend_buy_ml = platform.recommend_buy_ml  # ML-enhanced
    __main__.recommend_sell = platform.recommend_sell
    __main__.auto_trade_recommendation = platform.auto_trade_recommendation
    
    # Start (manual mode)
    platform.run()

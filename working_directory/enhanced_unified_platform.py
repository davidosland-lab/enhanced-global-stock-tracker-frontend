"""
Enhanced Unified Trading Platform with Manual Controls
======================================================

Integrates:
1. Paper Trading Coordinator (with real swing signals)
2. Manual Trading Controls
3. Web Dashboard with manual trade execution
4. Real-time monitoring

Usage:
    python enhanced_unified_platform.py --real-signals

Then visit: http://localhost:5000

Features:
- Automatic trading with 70-75% win rate signals
- Manual buy/sell controls
- Position management (adjust stop-loss, take-profit)
- Real-time dashboard
- Order validation
- Quote lookup

Author: Enhanced Global Stock Tracker
Date: December 25, 2024
"""

import sys
from pathlib import Path
import logging
import threading
import argparse
from flask import Flask, render_template
from flask_cors import CORS

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'phase3_intraday_deployment'))

# Import our modules
try:
    from paper_trading_coordinator import PaperTradingCoordinator
    COORDINATOR_AVAILABLE = True
except ImportError as e:
    logging.error(f"Could not import PaperTradingCoordinator: {e}")
    COORDINATOR_AVAILABLE = False

from manual_trading_controls import add_manual_trading_to_app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_platform.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedTradingPlatform:
    """
    Enhanced trading platform with manual controls
    """
    
    def __init__(
        self,
        symbols: list,
        initial_capital: float = 100000.0,
        use_real_signals: bool = True,
        port: int = 5000
    ):
        """Initialize platform"""
        self.symbols = symbols
        self.initial_capital = initial_capital
        self.use_real_signals = use_real_signals
        self.port = port
        
        # Initialize paper trading coordinator
        if COORDINATOR_AVAILABLE:
            logger.info("Initializing Paper Trading Coordinator...")
            self.coordinator = PaperTradingCoordinator(
                symbols=symbols,
                initial_capital=initial_capital,
                use_real_swing_signals=use_real_signals
            )
            
            # Store reference to engine for manual trading
            self.engine = self.coordinator
        else:
            logger.error("Paper Trading Coordinator not available!")
            raise ImportError("Cannot initialize without PaperTradingCoordinator")
        
        # Flask app
        self.app = Flask(__name__, template_folder='templates')
        CORS(self.app)
        
        # Setup routes
        self._setup_routes()
        
        # Add manual trading controls
        add_manual_trading_to_app(self.app, self)
        
        logger.info("Enhanced Trading Platform initialized")
        logger.info(f"  Real Signals: {use_real_signals}")
        logger.info(f"  Expected Win Rate: {'70-75%' if use_real_signals else '50-60%'}")
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Serve dashboard"""
            return render_template('dashboard_manual.html')
        
        @self.app.route('/api/summary')
        def api_summary():
            """Get portfolio summary"""
            try:
                from flask import jsonify
                from datetime import datetime
                
                status = self.coordinator.get_status_dict()
                
                return jsonify({
                    'status': 'online',
                    'paper_trading': True,
                    'market': 'US',
                    'portfolio': {
                        'capital': {
                            'total_value': status['capital']['total'],
                            'current_capital': status['capital']['cash'],
                            'invested': status['capital']['invested'],
                            'total_return_pct': status['capital']['total_return_pct']
                        },
                        'positions': {
                            'count': status['positions']['count']
                        },
                        'performance': {
                            'total_trades': status['performance']['total_trades'],
                            'win_rate': status['performance']['win_rate'],
                            'total_realized_pnl': status['performance']['realized_pnl'],
                            'max_drawdown': status['performance']['max_drawdown']
                        },
                        'risk': {
                            'portfolio_heat': 0.0  # Calculate if needed
                        }
                    },
                    'sentiment': {
                        'market': status['market']['sentiment'],
                        'macro': status['market']['sentiment'],
                        'combined': status['market']['sentiment']
                    },
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in api_summary: {e}", exc_info=True)
                from flask import jsonify
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/positions')
        def api_positions():
            """Get open positions"""
            try:
                from flask import jsonify
                from datetime import datetime
                
                positions = []
                for symbol, pos in self.coordinator.positions.items():
                    positions.append({
                        'symbol': symbol,
                        'shares': pos.shares,
                        'entry_price': pos.entry_price,
                        'current_price': pos.current_price,
                        'unrealized_pnl': pos.unrealized_pnl,
                        'unrealized_pnl_pct': pos.unrealized_pnl_pct,
                        'stop_loss': pos.stop_loss,
                        'take_profit': pos.profit_target if pos.profit_target else pos.entry_price * 1.15,
                        'entry_date': pos.entry_date
                    })
                
                return jsonify({
                    'positions': positions,
                    'count': len(positions),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in api_positions: {e}", exc_info=True)
                from flask import jsonify
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/alerts')
        def api_alerts():
            """Get recent alerts"""
            try:
                from flask import jsonify
                from datetime import datetime
                
                # Get recent intraday alerts if available
                alerts = []
                
                # Add from coordinator's state if available
                if hasattr(self.coordinator, 'intraday_alerts'):
                    for alert in self.coordinator.intraday_alerts[-10:]:
                        alerts.append({
                            'type': alert.get('type', 'info'),
                            'message': f"{alert.get('symbol', '')} - {alert.get('type', '')}",
                            'severity': 'info',
                            'timestamp': alert.get('timestamp', datetime.now().isoformat())
                        })
                
                return jsonify({
                    'alerts': alerts,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in api_alerts: {e}", exc_info=True)
                from flask import jsonify
                return jsonify({'error': str(e)}), 500
    
    def get_current_price(self, symbol: str):
        """Get current price for symbol"""
        return self.coordinator.fetch_current_price(symbol)
    
    def run_dashboard(self):
        """Run Flask dashboard"""
        logger.info(f"\n{'='*80}")
        logger.info(f"STARTING ENHANCED TRADING PLATFORM")
        logger.info(f"{'='*80}")
        logger.info(f"Dashboard URL: http://localhost:{self.port}")
        logger.info(f"Real Signals: {self.use_real_signals}")
        logger.info(f"Expected Win Rate: {'70-75%' if self.use_real_signals else '50-60%'}")
        logger.info(f"{'='*80}\n")
        
        # Run Flask in main thread (blocking)
        self.app.run(
            host='0.0.0.0',
            port=self.port,
            debug=False,
            use_reloader=False
        )
    
    def run_auto_trading(self):
        """Run automatic trading in background"""
        logger.info("Starting automatic trading cycle...")
        
        def trading_loop():
            try:
                while True:
                    self.coordinator.run_trading_cycle()
                    
                    import time
                    time.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"Error in trading loop: {e}", exc_info=True)
        
        # Start trading thread
        trading_thread = threading.Thread(target=trading_loop, daemon=True)
        trading_thread.start()
        
        logger.info("Automatic trading started in background")
    
    def run(self):
        """Run platform with both auto trading and manual controls"""
        # Start automatic trading in background
        self.run_auto_trading()
        
        # Run dashboard in main thread (blocking)
        self.run_dashboard()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Enhanced Unified Trading Platform with Manual Controls'
    )
    parser.add_argument(
        '--symbols',
        type=str,
        default='AAPL,GOOGL,MSFT,NVDA',
        help='Comma-separated list of symbols (default: AAPL,GOOGL,MSFT,NVDA)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=100000.0,
        help='Initial capital (default: 100000)'
    )
    parser.add_argument(
        '--real-signals',
        action='store_true',
        help='Use real SwingSignalGenerator (70-75%% win rate)'
    )
    parser.add_argument(
        '--simplified',
        action='store_true',
        help='Use simplified signals (50-60%% win rate)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Dashboard port (default: 5000)'
    )
    
    args = parser.parse_args()
    
    # Parse symbols
    symbols = [s.strip().upper() for s in args.symbols.split(',')]
    
    # Determine signal mode (default to real signals)
    use_real_signals = args.real_signals or not args.simplified
    
    # Create directories
    Path('logs').mkdir(exist_ok=True)
    Path('state').mkdir(exist_ok=True)
    
    # Create platform
    try:
        platform = EnhancedTradingPlatform(
            symbols=symbols,
            initial_capital=args.capital,
            use_real_signals=use_real_signals,
            port=args.port
        )
        
        # Run
        platform.run()
        
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

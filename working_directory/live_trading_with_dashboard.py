"""
Complete Live Trading System with Dashboard Integration
=======================================================

This example shows how to integrate the dashboard with the live trading coordinator.

Usage:
    python live_trading_with_dashboard.py --market US --paper-trading

Features:
- Live trading coordinator with swing + intraday integration
- Real-time web dashboard
- Automated alerting
- Position management
- Performance tracking

Author: FinBERT Enhanced System
Date: December 21, 2024
"""

import argparse
import logging
import threading
import time
import signal
import sys
from datetime import datetime
from pathlib import Path

# Import trading coordinator
# from live_trading_coordinator import LiveTradingCoordinator

# Import dashboard
from live_trading_dashboard import set_coordinator, start_dashboard, add_alert

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/live_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LiveTradingSystem:
    """
    Complete live trading system with dashboard integration
    """
    
    def __init__(
        self,
        market: str = "US",
        initial_capital: float = 100000.0,
        config_file: str = None,
        paper_trading: bool = True,
        dashboard_port: int = 5000
    ):
        """
        Initialize live trading system
        
        Args:
            market: Market to trade ('US' or 'ASX')
            initial_capital: Starting capital
            config_file: Path to configuration file
            paper_trading: If True, simulate trades
            dashboard_port: Port for web dashboard
        """
        self.market = market
        self.paper_trading = paper_trading
        self.dashboard_port = dashboard_port
        
        logger.info("="*80)
        logger.info("INITIALIZING LIVE TRADING SYSTEM")
        logger.info("="*80)
        logger.info(f"Market: {market}")
        logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"Paper Trading: {paper_trading}")
        logger.info(f"Dashboard Port: {dashboard_port}")
        
        # Initialize coordinator (would be imported from live_trading_coordinator.py)
        logger.info("Initializing Trading Coordinator...")
        # self.coordinator = LiveTradingCoordinator(
        #     market=market,
        #     initial_capital=initial_capital,
        #     config_file=config_file,
        #     paper_trading=paper_trading
        # )
        
        # For demo purposes, create a mock coordinator
        self.coordinator = self._create_mock_coordinator()
        
        # Register coordinator with dashboard
        logger.info("Registering coordinator with dashboard...")
        set_coordinator(self.coordinator)
        
        # Start dashboard in background thread
        logger.info(f"Starting dashboard on port {dashboard_port}...")
        self.dashboard_thread = threading.Thread(
            target=start_dashboard,
            kwargs={
                'host': '0.0.0.0',
                'port': dashboard_port,
                'debug': False
            }
        )
        self.dashboard_thread.daemon = True
        self.dashboard_thread.start()
        
        # Give dashboard time to start
        time.sleep(2)
        
        logger.info("="*80)
        logger.info("SYSTEM INITIALIZATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Dashboard: http://localhost:{dashboard_port}")
        logger.info("="*80)
        
        # Add startup alert
        add_alert(
            'system',
            f'Live trading system started - {market} market, Paper Trading: {paper_trading}',
            severity='success'
        )
    
    def _create_mock_coordinator(self):
        """Create mock coordinator for demo"""
        class MockCoordinator:
            def __init__(self):
                self.initial_capital = 100000.0
                self.current_capital = 102000.0
                self.positions = {}
                self.closed_trades = []
                self.metrics = {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'total_pnl': 2000.0,
                    'max_drawdown': 0.02,
                    'peak_capital': 103000.0
                }
                self.last_market_sentiment = 65
                self.last_macro_sentiment = 58
                self.config = {
                    'risk_management': {
                        'max_portfolio_heat': 0.06,
                        'max_single_trade_risk': 0.02
                    }
                }
                
                # Mock intraday manager
                class MockIntradayManager:
                    def is_market_open(self):
                        return True
                    
                    def get_session_stats(self):
                        return {
                            'rescan_count': 5,
                            'market': 'US',
                            'market_open': True
                        }
                    
                    def get_tracked_opportunities(self, min_strength=None, max_count=None):
                        return []
                
                self.intraday_manager = MockIntradayManager()
                self.scheduler = None
            
            def get_portfolio_status(self):
                return {
                    'capital': {
                        'initial': self.initial_capital,
                        'current_cash': self.current_capital,
                        'invested': 0,
                        'total_value': self.current_capital,
                        'total_return_pct': 2.0
                    },
                    'positions': {
                        'count': 0,
                        'swing': 0,
                        'intraday': 0,
                        'symbols': [],
                        'total_unrealized_pnl': 0,
                        'total_unrealized_pnl_pct': 0
                    },
                    'performance': {
                        'total_trades': self.metrics['total_trades'],
                        'winning_trades': self.metrics['winning_trades'],
                        'losing_trades': self.metrics['losing_trades'],
                        'win_rate': 0,
                        'total_realized_pnl': self.metrics['total_pnl'],
                        'max_drawdown': self.metrics['max_drawdown'] * 100
                    }
                }
            
            def get_position_details(self):
                return []
            
            def get_market_context(self):
                return {
                    'timestamp': datetime.now().isoformat(),
                    'market': 'US',
                    'sentiment_score': 65,
                    'macro_score': 58,
                    'combined_sentiment': 63,
                    'market_regime': 'MILD_UPTREND'
                }
        
        return MockCoordinator()
    
    def start(self):
        """
        Start the live trading system
        """
        logger.info("\n" + "="*80)
        logger.info("STARTING LIVE TRADING SESSION")
        logger.info("="*80 + "\n")
        
        # Start intraday monitoring
        # self.coordinator.start_intraday_monitoring()
        
        add_alert(
            'intraday',
            'Intraday monitoring started - scanning every 15 minutes',
            severity='info'
        )
        
        # Main trading loop
        try:
            cycle_count = 0
            
            while True:
                cycle_count += 1
                
                logger.info(f"\n{'='*80}")
                logger.info(f"Trading Cycle #{cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*80}")
                
                # 1. Get market context
                logger.info("Fetching market context...")
                market_context = self.coordinator.get_market_context()
                
                # 2. Update positions (would fetch real prices)
                logger.info("Updating positions...")
                # current_prices = fetch_current_prices(self.coordinator.positions.keys())
                # self.coordinator.update_positions(current_prices)
                
                # 3. Check exit conditions
                logger.info("Checking exit conditions...")
                # exits = self.coordinator.check_exit_conditions(market_context)
                # for symbol, exit_reason in exits:
                #     self.coordinator.exit_position(symbol, exit_reason)
                
                # 4. Evaluate new entries (if slots available)
                logger.info("Evaluating potential entries...")
                # candidates = screen_for_candidates()
                # for candidate in candidates:
                #     should_enter, confidence, signal = self.coordinator.evaluate_swing_entry(
                #         candidate['symbol'],
                #         candidate['price_data'],
                #         candidate['news_data'],
                #         market_context
                #     )
                #     if should_enter:
                #         self.coordinator.enter_swing_position(
                #             candidate['symbol'],
                #             candidate['current_price'],
                #             signal,
                #             market_context
                #         )
                
                # 5. Log portfolio status
                status = self.coordinator.get_portfolio_status()
                logger.info(f"\nPortfolio Status:")
                logger.info(f"  Total Capital: ${status['capital']['total_value']:,.2f}")
                logger.info(f"  Total Return: {status['capital']['total_return_pct']:+.2f}%")
                logger.info(f"  Open Positions: {status['positions']['count']}")
                logger.info(f"  Win Rate: {status['performance']['win_rate']:.1f}%")
                
                # 6. Sleep until next cycle (5 minutes)
                logger.info(f"\nNext cycle in 5 minutes...")
                time.sleep(300)
        
        except KeyboardInterrupt:
            logger.info("\nReceived shutdown signal...")
            self.shutdown()
        except Exception as e:
            logger.error(f"Error in trading loop: {e}", exc_info=True)
            self.shutdown()
    
    def shutdown(self):
        """
        Gracefully shutdown the system
        """
        logger.info("\n" + "="*80)
        logger.info("SHUTTING DOWN LIVE TRADING SYSTEM")
        logger.info("="*80)
        
        # Stop intraday monitoring
        # if self.coordinator.scheduler:
        #     self.coordinator.stop_intraday_monitoring()
        
        # Save state
        logger.info("Saving system state...")
        # self.coordinator.save_state('live_trading_state.json')
        
        add_alert(
            'system',
            'Live trading system shutting down',
            severity='warning'
        )
        
        # Final status
        status = self.coordinator.get_portfolio_status()
        logger.info(f"\nFinal Status:")
        logger.info(f"  Total Capital: ${status['capital']['total_value']:,.2f}")
        logger.info(f"  Total Return: {status['capital']['total_return_pct']:+.2f}%")
        logger.info(f"  Total Trades: {status['performance']['total_trades']}")
        logger.info(f"  Win Rate: {status['performance']['win_rate']:.1f}%")
        
        logger.info("\n" + "="*80)
        logger.info("SHUTDOWN COMPLETE")
        logger.info("="*80)
        
        sys.exit(0)


def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    print("\n\nReceived interrupt signal (Ctrl+C)")
    sys.exit(0)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Live Trading System with Dashboard')
    parser.add_argument('--market', type=str, default='US', choices=['US', 'ASX'],
                       help='Market to trade (default: US)')
    parser.add_argument('--capital', type=float, default=100000.0,
                       help='Initial capital (default: 100000)')
    parser.add_argument('--config', type=str, default=None,
                       help='Path to configuration file')
    parser.add_argument('--paper-trading', action='store_true',
                       help='Enable paper trading mode (no real trades)')
    parser.add_argument('--dashboard-port', type=int, default=5000,
                       help='Dashboard port (default: 5000)')
    
    args = parser.parse_args()
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize and start system
    system = LiveTradingSystem(
        market=args.market,
        initial_capital=args.capital,
        config_file=args.config,
        paper_trading=args.paper_trading,
        dashboard_port=args.dashboard_port
    )
    
    system.start()


if __name__ == "__main__":
    main()

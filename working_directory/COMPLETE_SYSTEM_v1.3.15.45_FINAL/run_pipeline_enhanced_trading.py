# -*- coding: utf-8 -*-
"""
Pipeline-Enhanced Paper Trading System
=======================================

Automated trading system that combines:
1. Overnight pipeline sentiment analysis (AU/US/UK markets)
2. Flexible position sizing based on opportunity/risk
3. ML-based signal generation (SwingSignalGenerator)
4. Real-time intraday monitoring

Usage:
    # Run with pipeline integration
    python run_pipeline_enhanced_trading.py --market UK --capital 100000
    
    # Run multi-market mode
    python run_pipeline_enhanced_trading.py --markets AU,US,UK --capital 200000
    
    # Dry run (no actual trades)
    python run_pipeline_enhanced_trading.py --market US --dry-run

Features:
- Morning sentiment analysis informs opening positions
- Dynamic position sizing (5%-30% based on sentiment)
- Opportunity mode for strong signals (sentiment ≥70)
- Risk override for elevated volatility
- Compatible with existing paper trading infrastructure
"""

import logging
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline_enhanced_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import components
from pipeline_signal_adapter import PipelineSignalAdapter
from paper_trading_coordinator import PaperTradingCoordinator


class PipelineEnhancedTrading:
    """
    Enhanced trading system that uses pipeline overnight sentiment
    to inform trading decisions with flexible position sizing.
    """
    
    def __init__(
        self,
        markets: List[str],
        initial_capital: float = 100000,
        dry_run: bool = False,
        config_path: Optional[str] = None
    ):
        """
        Initialize pipeline-enhanced trading system
        
        Args:
            markets: List of markets to trade ('AU', 'US', 'UK')
            initial_capital: Starting capital
            dry_run: If True, generate signals but don't execute trades
            config_path: Path to trading configuration
        """
        self.markets = markets
        self.initial_capital = initial_capital
        self.dry_run = dry_run
        
        logger.info("="*80)
        logger.info("PIPELINE-ENHANCED TRADING SYSTEM")
        logger.info("="*80)
        logger.info(f"Markets: {', '.join(markets)}")
        logger.info(f"Capital: ${initial_capital:,.2f}")
        logger.info(f"Dry Run: {dry_run}")
        
        # Initialize pipeline signal adapter
        self.signal_adapter = PipelineSignalAdapter(config_path=config_path)
        logger.info("[OK] Pipeline signal adapter initialized")
        
        # Initialize paper trading coordinator
        self.coordinator = PaperTradingCoordinator(
            initial_capital=initial_capital,
            config_file=config_path or 'config/live_trading_config.json'
        )
        logger.info("[OK] Paper trading coordinator initialized")
        
        # Track today's signals
        self.todays_signals = {}
        self.signal_timestamp = None
    
    def fetch_morning_signals(self, force_refresh: bool = False) -> Dict[str, List]:
        """
        Fetch morning signals from all tracked markets
        
        Args:
            force_refresh: Force refresh even if cached
            
        Returns:
            Dictionary of {market: [signals]}
        """
        # Check if we already fetched signals today
        if not force_refresh and self.signal_timestamp:
            if self.signal_timestamp.date() == datetime.now().date():
                logger.info("Using cached morning signals from today")
                return self.todays_signals
        
        logger.info("="*80)
        logger.info("FETCHING MORNING SIGNALS")
        logger.info("="*80)
        
        # Get signals from all markets
        all_signals = self.signal_adapter.get_all_market_signals(
            markets=self.markets,
            max_signals_per_market=5
        )
        
        # Cache the signals
        self.todays_signals = all_signals
        self.signal_timestamp = datetime.now()
        
        # Log summary
        total_signals = sum(len(signals) for signals in all_signals.values())
        logger.info(f"\nTotal signals generated: {total_signals}")
        for market, signals in all_signals.items():
            logger.info(f"  {market}: {len(signals)} signals")
        
        return all_signals
    
    def execute_morning_signals(self, max_positions: int = 10) -> Dict:
        """
        Execute morning signals (opening positions based on overnight sentiment)
        
        Args:
            max_positions: Maximum number of positions to open
            
        Returns:
            Execution summary
        """
        logger.info("="*80)
        logger.info("EXECUTING MORNING SIGNALS")
        logger.info("="*80)
        
        # Fetch signals
        all_signals = self.fetch_morning_signals()
        
        if not all_signals:
            logger.warning("No signals available")
            return {'status': 'no_signals', 'positions_opened': 0}
        
        # Flatten all signals and sort by confidence
        flat_signals = []
        for market, signals in all_signals.items():
            flat_signals.extend(signals)
        
        # Sort by sentiment score (highest first)
        flat_signals.sort(key=lambda s: s.sentiment_score, reverse=True)
        
        # Limit to max positions
        selected_signals = flat_signals[:max_positions]
        
        logger.info(f"\nSelected {len(selected_signals)} signals for execution")
        
        # Execute each signal
        results = {
            'total_signals': len(selected_signals),
            'positions_opened': 0,
            'positions_skipped': 0,
            'errors': []
        }
        
        for signal in selected_signals:
            try:
                logger.info(f"\n{'─'*60}")
                logger.info(f"Signal: {signal.symbol} ({signal.market})")
                logger.info(f"  Action: {signal.action}")
                logger.info(f"  Sentiment: {signal.sentiment_score:.1f}/100")
                logger.info(f"  Position Size: {signal.adjusted_position_size:.1%}")
                logger.info(f"  Stop Loss: {signal.stop_loss_pct:.1%}")
                logger.info(f"  Take Profit: {signal.take_profit_pct:.1%}")
                
                if self.dry_run:
                    logger.info("  [DRY RUN] Would execute signal")
                    results['positions_skipped'] += 1
                    continue
                
                if signal.action == 'BUY':
                    # Format signal for coordinator
                    formatted_signal = {
                        'symbol': signal.symbol,
                        'signal': 'BUY',
                        'confidence': signal.confidence / 100.0,
                        'reason': signal.entry_reason,
                        'source': 'pipeline_enhanced',
                        'stop_loss': signal.stop_loss_pct,
                        'take_profit': signal.take_profit_pct,
                        'position_size': signal.adjusted_position_size,
                        'sentiment_score': signal.sentiment_score
                    }
                    
                    # Enter position via coordinator
                    success = self.coordinator.enter_position(signal.symbol, formatted_signal)
                    
                    if success:
                        results['positions_opened'] += 1
                        logger.info("  [OK] Position opened successfully")
                    else:
                        results['positions_skipped'] += 1
                        logger.warning("  [X] Position not opened (coordinator rejected)")
                
                elif signal.action in ['SELL', 'REDUCE']:
                    # Check if we have position to exit
                    if signal.symbol in self.coordinator.positions:
                        logger.info("  Action: EXIT existing position")
                        success = self.coordinator.exit_position(
                            signal.symbol,
                            exit_reason=f"Pipeline signal: {signal.pipeline_recommendation}"
                        )
                        if success:
                            results['positions_opened'] += 1  # Count as action taken
                            logger.info("  [OK] Position exited successfully")
                    else:
                        logger.info("  No existing position to exit")
                        results['positions_skipped'] += 1
                
            except Exception as e:
                logger.error(f"Error executing signal for {signal.symbol}: {e}")
                results['errors'].append({
                    'symbol': signal.symbol,
                    'error': str(e)
                })
                results['positions_skipped'] += 1
        
        logger.info("="*80)
        logger.info("EXECUTION SUMMARY")
        logger.info("="*80)
        logger.info(f"Total Signals: {results['total_signals']}")
        logger.info(f"Positions Opened: {results['positions_opened']}")
        logger.info(f"Positions Skipped: {results['positions_skipped']}")
        logger.info(f"Errors: {len(results['errors'])}")
        
        return results
    
    def run_continuous_monitoring(self, interval_minutes: int = 15):
        """
        Run continuous monitoring with intraday scans
        
        Args:
            interval_minutes: Minutes between intraday scans
        """
        logger.info("="*80)
        logger.info("STARTING CONTINUOUS MONITORING")
        logger.info("="*80)
        logger.info(f"Interval: {interval_minutes} minutes")
        
        try:
            # Execute morning signals first
            self.execute_morning_signals()
            
            # Run coordinator's continuous monitoring
            # (This handles position updates, exits, intraday scans)
            self.coordinator.run_trading_cycle()
            
        except KeyboardInterrupt:
            logger.info("\nShutting down gracefully...")
            self.print_final_summary()
        except Exception as e:
            logger.error(f"Error in continuous monitoring: {e}")
            import traceback
            traceback.print_exc()
    
    def run_once(self):
        """
        Run a single cycle (fetch signals, execute, update positions)
        """
        logger.info("="*80)
        logger.info("RUNNING SINGLE CYCLE")
        logger.info("="*80)
        
        # Execute morning signals
        execution_results = self.execute_morning_signals()
        
        # Update existing positions
        self.coordinator.update_positions()
        
        # Check for exits
        exits = self.coordinator.check_exits()
        logger.info(f"\nExits triggered: {len(exits)}")
        
        # Print status
        self.print_status()
        
        return execution_results
    
    def print_status(self):
        """Print current system status"""
        logger.info("="*80)
        logger.info("SYSTEM STATUS")
        logger.info("="*80)
        
        # Pipeline sentiment summary
        logger.info("\nMorning Sentiment:")
        for market in self.markets:
            sentiment = self.signal_adapter.get_morning_sentiment(market)
            if sentiment:
                logger.info(f"  {market}: {sentiment.sentiment_score:.1f}/100 - {sentiment.recommendation}")
        
        # Trading coordinator status
        logger.info(f"\nPortfolio:")
        logger.info(f"  Capital: ${self.coordinator.capital:,.2f}")
        logger.info(f"  Positions: {len(self.coordinator.positions)}")
        
        if self.coordinator.positions:
            logger.info(f"\n  Open Positions:")
            for symbol, position in self.coordinator.positions.items():
                current_price = self.coordinator.fetch_current_price(symbol)
                if current_price:
                    pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
                    logger.info(f"    {symbol}: {position.quantity} @ ${position.entry_price:.2f} "
                              f"(P/L: {pnl_pct:+.2f}%)")
    
    def print_final_summary(self):
        """Print final summary before shutdown"""
        logger.info("="*80)
        logger.info("FINAL SUMMARY")
        logger.info("="*80)
        
        # Print coordinator status
        self.coordinator.print_status()
        
        # Generate tax report if available
        if hasattr(self.coordinator, 'generate_tax_report'):
            try:
                report_path = self.coordinator.generate_tax_report()
                if report_path:
                    logger.info(f"\n[OK] Tax report generated: {report_path}")
            except Exception as e:
                logger.warning(f"Could not generate tax report: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Pipeline-Enhanced Paper Trading System'
    )
    parser.add_argument(
        '--market',
        type=str,
        help='Single market to trade (AU, US, or UK)'
    )
    parser.add_argument(
        '--markets',
        type=str,
        help='Comma-separated markets to trade (e.g., AU,US,UK)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=100000,
        help='Initial capital (default: 100000)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate signals but don\'t execute trades'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (don\'t start continuous monitoring)'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Determine markets
    if args.markets:
        markets = [m.strip().upper() for m in args.markets.split(',')]
    elif args.market:
        markets = [args.market.upper()]
    else:
        markets = ['US']  # Default to US market
    
    # Validate markets
    valid_markets = ['AU', 'US', 'UK']
    for market in markets:
        if market not in valid_markets:
            logger.error(f"Invalid market: {market}. Valid options: {', '.join(valid_markets)}")
            sys.exit(1)
    
    # Initialize system
    system = PipelineEnhancedTrading(
        markets=markets,
        initial_capital=args.capital,
        dry_run=args.dry_run,
        config_path=args.config
    )
    
    # Run
    if args.once:
        system.run_once()
    else:
        system.run_continuous_monitoring()


if __name__ == "__main__":
    main()

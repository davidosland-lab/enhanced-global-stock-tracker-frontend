#!/usr/bin/env python3
"""
RIO.AX Backtest - FULL Phase 3 ML Stack
========================================

Tests the complete Phase 3 trading system with:
- FinBERT Sentiment Analysis (25%)
- LSTM Neural Networks (25%)
- Technical Analysis (25%)
- Momentum Analysis (15%)
- Volume Analysis (10%)

Plus Phase 3 features:
- Intraday monitoring simulation
- 5-day hold OR +8% OR -3% exits
- 25% position sizing, max 3 concurrent
- Market sentiment blocking/boosting

Symbol: RIO.AX (Rio Tinto)
Period: 2 years
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from backtest_cba_phase3_integrated import Phase3BacktestEngine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Calculate 2-year period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    logger.info("="*80)
    logger.info("RIO.AX 2-YEAR BACKTEST - FULL PHASE 3 ML STACK")
    logger.info("="*80)
    logger.info(f"Symbol: RIO.AX (Rio Tinto Limited)")
    logger.info(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"Initial Capital: $100,000 AUD")
    logger.info("")
    logger.info("ML Components (5-Component System):")
    logger.info("  ✓ FinBERT Sentiment Analysis (25%)")
    logger.info("  ✓ LSTM Neural Networks (25%)")
    logger.info("  ✓ Technical Analysis (25%)")
    logger.info("  ✓ Momentum Analysis (15%)")
    logger.info("  ✓ Volume Analysis (10%)")
    logger.info("")
    logger.info("Phase 3 Strategy:")
    logger.info("  • Entry: ML confidence ≥ 55%")
    logger.info("  • Exit: 5 days OR +8% profit OR -3% stop")
    logger.info("  • Position: 25% sizing, max 3 concurrent")
    logger.info("  • Market: Sentiment blocking (< 30) & boosting (> 70)")
    logger.info("="*80)
    logger.info("")
    
    # Initialize backtest engine with FULL ML
    engine = Phase3BacktestEngine(
        symbol='RIO.AX',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=100000.0,
        use_ml=True  # FULL ML STACK
    )
    
    # Fetch data
    logger.info("Fetching historical data for RIO.AX...")
    historical_data = engine.fetch_historical_data()
    
    if historical_data is None or historical_data.empty:
        logger.error("Failed to fetch data - cannot run backtest")
        return 1
    
    # Analyze stock characteristics
    prices = historical_data['Close']
    start_price = prices.iloc[0]
    end_price = prices.iloc[-1]
    low_price = prices.min()
    high_price = prices.max()
    avg_price = prices.mean()
    
    returns = prices.pct_change().dropna()
    volatility = returns.std() * (252 ** 0.5) * 100  # Annualized
    
    buy_hold_return = ((end_price - start_price) / start_price) * 100
    
    logger.info(f"")
    logger.info(f"RIO.AX Stock Analysis ({len(historical_data)} days):")
    logger.info(f"  Start Price:  ${start_price:.2f}")
    logger.info(f"  End Price:    ${end_price:.2f}")
    logger.info(f"  Low:          ${low_price:.2f}")
    logger.info(f"  High:         ${high_price:.2f}")
    logger.info(f"  Average:      ${avg_price:.2f}")
    logger.info(f"  Buy & Hold:   {buy_hold_return:+.2f}%")
    logger.info(f"  Volatility:   {volatility:.2f}% (annualized)")
    logger.info(f"")
    
    # Run backtest with FULL ML
    logger.info("Running Phase 3 backtest with FULL ML stack...")
    logger.info("")
    engine.run_backtest(historical_data)
    
    # Generate report
    performance = engine.print_report()
    
    # Save results
    engine.save_results('backtest_rio_phase3_results.json')
    
    # Compare with benchmarks
    logger.info("")
    logger.info("="*80)
    logger.info("COMPARISON")
    logger.info("="*80)
    logger.info(f"Buy & Hold Strategy:     {buy_hold_return:+.2f}%")
    logger.info(f"Phase 3 ML Strategy:     {performance['total_return']:+.2f}%")
    logger.info(f"")
    logger.info(f"Active Trading Results:")
    logger.info(f"  Total Trades:    {performance['total_trades']}")
    logger.info(f"  Win Rate:        {performance['win_rate']:.2f}%")
    logger.info(f"  Profit Factor:   {performance['profit_factor']:.2f}")
    logger.info(f"  Max Drawdown:    {performance['max_drawdown']:.2f}%")
    logger.info(f"  Sharpe Ratio:    {performance['sharpe_ratio']:.2f}")
    logger.info("="*80)
    logger.info("")
    
    # Final assessment
    if performance['total_trades'] > 0:
        if performance['win_rate'] >= 60 and performance['total_return'] > 0:
            logger.info("✅ EXCELLENT: Model met Phase 3 targets (60%+ win rate)")
        elif performance['win_rate'] >= 50 and performance['total_return'] > 0:
            logger.info("✓ GOOD: Model performed well")
        else:
            logger.info("⚠ REVIEW: Model needs optimization")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

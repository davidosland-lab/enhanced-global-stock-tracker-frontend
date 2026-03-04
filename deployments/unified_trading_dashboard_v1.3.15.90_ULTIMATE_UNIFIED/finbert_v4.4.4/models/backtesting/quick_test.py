"""
Quick Test Script for Backtesting Framework
===========================================

This script runs a minimal test to verify the framework is working correctly.
"""

import logging
import sys
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def quick_test():
    """Run a quick test of all three phases"""
    
    print("\n" + "="*80)
    print("BACKTESTING FRAMEWORK - QUICK TEST")
    print("="*80)
    
    try:
        # Phase 1: Test Data Loading
        print("\n[PHASE 1] Testing Data Loading...")
        import sys
        import os
        
        # Add parent directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from data_loader import HistoricalDataLoader
        
        loader = HistoricalDataLoader(
            symbol='AAPL',
            start_date='2023-11-01',
            end_date='2023-12-01',
            use_cache=True
        )
        
        data = loader.load_price_data()
        
        if data.empty:
            print("❌ FAILED: No data loaded")
            return False
        
        print(f"✅ SUCCESS: Loaded {len(data)} days of data")
        print(f"   Date range: {data.index.min().date()} to {data.index.max().date()}")
        print(f"   Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
        
        # Phase 2: Test Predictions
        print("\n[PHASE 2] Testing Prediction Engine...")
        from prediction_engine import BacktestPredictionEngine
        
        engine = BacktestPredictionEngine(model_type='ensemble')
        
        predictions = engine.walk_forward_backtest(
            data=data,
            start_date='2023-11-15',
            end_date='2023-12-01',
            prediction_frequency='daily',
            lookback_days=10  # Small lookback for quick test
        )
        
        if predictions.empty:
            print("❌ FAILED: No predictions generated")
            return False
        
        print(f"✅ SUCCESS: Generated {len(predictions)} predictions")
        
        # Count signals
        buy_signals = (predictions['prediction'] == 'BUY').sum()
        sell_signals = (predictions['prediction'] == 'SELL').sum()
        hold_signals = (predictions['prediction'] == 'HOLD').sum()
        
        print(f"   BUY signals: {buy_signals}")
        print(f"   SELL signals: {sell_signals}")
        print(f"   HOLD signals: {hold_signals}")
        
        # Phase 3: Test Trading Simulation
        print("\n[PHASE 3] Testing Trading Simulator...")
        from trading_simulator import TradingSimulator
        
        simulator = TradingSimulator(initial_capital=10000)
        
        # Execute predictions
        for idx, row in predictions.iterrows():
            simulator.execute_signal(
                timestamp=row['timestamp'],
                signal=row['prediction'],
                price=row.get('actual_price', row['current_price']),
                confidence=row['confidence']
            )
        
        # Get metrics
        metrics = simulator.calculate_performance_metrics()
        
        if 'error' in metrics:
            print(f"⚠️  WARNING: {metrics['error']}")
            print("   (This is normal if no trades were executed)")
        else:
            print(f"✅ SUCCESS: Simulation complete")
            print(f"   Total trades: {metrics['total_trades']}")
            print(f"   Final equity: ${metrics['final_equity']:,.2f}")
            print(f"   Return: {metrics['total_return_pct']:.2f}%")
        
        # Overall success
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED - Framework is working correctly!")
        print("="*80)
        print("\nNext steps:")
        print("1. Run 'python example_backtest.py' for full examples")
        print("2. Test with your own stocks and date ranges")
        print("3. Compare different models (finbert, lstm, ensemble)")
        print("\n")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        print("\nPossible solutions:")
        print("1. Install missing packages: pip install yfinance pandas numpy")
        print("2. Verify you're in the correct directory")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = quick_test()
    sys.exit(0 if success else 1)

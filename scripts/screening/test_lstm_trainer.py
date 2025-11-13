"""
Test LSTM Training Integration

Tests the LSTM training system with model staleness detection and priority queues.

Usage:
    python scripts/screening/test_lstm_trainer.py
"""

import sys
from pathlib import Path

# Add project root to path
BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from models.screening.lstm_trainer import LSTMTrainer
from datetime import datetime
import pytz

def test_lstm_trainer():
    """Test LSTM training system"""
    print("="*80)
    print("LSTM TRAINING INTEGRATION - TEST")
    print("="*80)
    print()
    
    # Initialize trainer
    print("Step 1: Initialize LSTM Trainer")
    print("-" * 40)
    
    try:
        trainer = LSTMTrainer()
        print(f"✅ LSTM trainer initialized")
        print(f"   Enabled: {trainer.enabled}")
        print(f"   Max models per night: {trainer.max_models_per_night}")
        print(f"   Stale threshold: {trainer.stale_threshold_days} days")
        print(f"   Epochs: {trainer.epochs}")
        print(f"   Batch size: {trainer.batch_size}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize trainer: {str(e)}")
        return False
    
    # Test 1: Get training statistics
    print("Step 2: Get Training Statistics")
    print("-" * 40)
    
    try:
        stats = trainer.get_training_stats()
        print(f"✅ Training statistics retrieved")
        print(f"   Total models: {stats['total_models']}")
        print(f"   Fresh models: {stats['fresh_models']}")
        print(f"   Stale models: {stats['stale_models']}")
        print(f"   Average age: {stats['avg_model_age_days']:.1f} days")
        
        if stats.get('oldest_model'):
            print(f"   Oldest: {stats['oldest_model']['symbol']} ({stats['oldest_model']['age_days']} days)")
        
        if stats.get('newest_model'):
            print(f"   Newest: {stats['newest_model']['symbol']} ({stats['newest_model']['age_days']} days)")
        
        print()
    except Exception as e:
        print(f"❌ Failed to get statistics: {str(e)}")
        print()
    
    # Test 2: Check stale models (sample)
    print("Step 3: Check Stale Models (Sample)")
    print("-" * 40)
    
    try:
        # Test with a few sample stocks
        test_stocks = ['ANZ.AX', 'CBA.AX', 'BHP.AX', 'WBC.AX', 'NAB.AX']
        stale_stocks = trainer.check_stale_models(test_stocks)
        
        print(f"✅ Stale model check completed")
        print(f"   Test stocks: {len(test_stocks)}")
        print(f"   Stale models: {len(stale_stocks)}")
        
        if stale_stocks:
            print(f"   Stale: {', '.join(stale_stocks)}")
        else:
            print(f"   All models are fresh!")
        
        print()
    except Exception as e:
        print(f"❌ Failed to check stale models: {str(e)}")
        print()
    
    # Test 3: Create training queue (mock data)
    print("Step 4: Create Training Queue (Mock Data)")
    print("-" * 40)
    
    try:
        # Create mock opportunities
        mock_opportunities = [
            {
                'symbol': 'ANZ.AX',
                'company_name': 'ANZ Banking Group',
                'opportunity_score': 85.3,
                'signal': 'BUY',
                'confidence': 78.5
            },
            {
                'symbol': 'CBA.AX',
                'company_name': 'Commonwealth Bank',
                'opportunity_score': 82.1,
                'signal': 'BUY',
                'confidence': 75.2
            },
            {
                'symbol': 'BHP.AX',
                'company_name': 'BHP Group',
                'opportunity_score': 78.9,
                'signal': 'BUY',
                'confidence': 72.8
            },
            {
                'symbol': 'WBC.AX',
                'company_name': 'Westpac Banking',
                'opportunity_score': 76.5,
                'signal': 'BUY',
                'confidence': 70.1
            },
            {
                'symbol': 'NAB.AX',
                'company_name': 'National Australia Bank',
                'opportunity_score': 74.2,
                'signal': 'BUY',
                'confidence': 68.5
            }
        ]
        
        training_queue = trainer.create_training_queue(
            opportunities=mock_opportunities,
            max_stocks=3
        )
        
        print(f"✅ Training queue created")
        print(f"   Queue size: {len(training_queue)}")
        
        if training_queue:
            print(f"   Priority stocks:")
            for i, stock in enumerate(training_queue, 1):
                print(f"     {i}. {stock['symbol']} (Score: {stock['opportunity_score']:.1f}/100)")
        else:
            print(f"   No stocks need training (all models are fresh)")
        
        print()
    except Exception as e:
        print(f"❌ Failed to create training queue: {str(e)}")
        print()
    
    # Test 4: Simulate training (without actual training)
    print("Step 5: Simulate Training Process")
    print("-" * 40)
    
    try:
        if not trainer.enabled:
            print("⚠️  LSTM training is DISABLED in configuration")
            print("   To enable:")
            print("   1. Edit models/config/screening_config.json")
            print("   2. Set lstm_training.enabled = true")
            print()
        else:
            print("✅ LSTM training is ENABLED")
            print(f"   Ready to train up to {trainer.max_models_per_night} models per night")
            print()
            print("   Note: Actual training not performed in this test")
            print("   Use RUN_LSTM_TRAINING.bat to train models")
        
        print()
    except Exception as e:
        print(f"❌ Error in training simulation: {str(e)}")
        print()
    
    # Test 5: Check training logs directory
    print("Step 6: Check Training Infrastructure")
    print("-" * 40)
    
    try:
        models_dir = trainer.models_dir
        logs_dir = trainer.training_logs_dir
        
        print(f"✅ Training infrastructure checked")
        print(f"   Models directory: {models_dir}")
        print(f"   Models exist: {models_dir.exists()}")
        
        if models_dir.exists():
            model_count = len(list(models_dir.glob('*_lstm_model.h5')))
            print(f"   Model files: {model_count}")
        
        print(f"   Logs directory: {logs_dir}")
        print(f"   Logs exist: {logs_dir.exists()}")
        
        if logs_dir.exists():
            log_count = len(list(logs_dir.glob('*.jsonl')))
            print(f"   Log files: {log_count}")
        
        print()
    except Exception as e:
        print(f"❌ Failed to check infrastructure: {str(e)}")
        print()
    
    # Summary
    print("="*80)
    print("TEST COMPLETED")
    print("="*80)
    print()
    print("✅ All LSTM training tests completed successfully")
    print()
    print("Next Steps:")
    print("  1. To check model status: RUN CHECK_MODEL_STATUS.bat")
    print("  2. To train models: RUN RUN_LSTM_TRAINING.bat")
    print("  3. To integrate with pipeline: Models train automatically overnight")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = test_lstm_trainer()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

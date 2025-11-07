"""
LSTM Training Integration Module

Manages automated LSTM model training for the overnight screening system.
Detects stale models and trains priority stocks based on opportunity scores.

Features:
- Model staleness detection (>7 days old)
- Priority-based training queue (top 20 stocks by score)
- Progress tracking and logging
- Training statistics and performance metrics
- Integration with overnight pipeline
"""

import json
import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import traceback

# Setup logging
BASE_PATH = Path(__file__).parent.parent.parent
log_dir = BASE_PATH / 'logs' / 'screening'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'lstm_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LSTMTrainer:
    """
    Manages automated LSTM model training for priority stocks.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the LSTM trainer.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.timezone = pytz.timezone('Australia/Sydney')
        
        # Load configuration
        if config_path is None:
            config_path = BASE_PATH / 'models' / 'config' / 'screening_config.json'
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Training configuration
        self.training_config = self.config.get('lstm_training', {})
        self.enabled = self.training_config.get('enabled', True)
        self.max_models_per_night = self.training_config.get('max_models_per_night', 20)
        self.stale_threshold_days = self.training_config.get('stale_threshold_days', 7)
        self.epochs = self.training_config.get('epochs', 50)
        self.batch_size = self.training_config.get('batch_size', 32)
        self.validation_split = self.training_config.get('validation_split', 0.2)
        self.priority_strategy = self.training_config.get('priority_strategy', 'highest_opportunity_score')
        
        # Paths
        self.models_dir = BASE_PATH / 'models' / 'lstm'
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.training_logs_dir = BASE_PATH / 'logs' / 'lstm_training'
        self.training_logs_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"LSTM Trainer initialized (enabled: {self.enabled})")
        logger.info(f"Max models per night: {self.max_models_per_night}")
        logger.info(f"Stale threshold: {self.stale_threshold_days} days")
    
    def check_stale_models(self, stocks: List[str]) -> List[str]:
        """
        Check which stock models are stale (older than threshold).
        
        Args:
            stocks: List of stock symbols to check
        
        Returns:
            List of stock symbols with stale models
        """
        stale_stocks = []
        current_time = datetime.now(self.timezone)
        threshold_time = current_time - timedelta(days=self.stale_threshold_days)
        
        logger.info(f"Checking {len(stocks)} stocks for stale models...")
        logger.info(f"Threshold: {self.stale_threshold_days} days ({threshold_time.strftime('%Y-%m-%d %H:%M:%S')})")
        
        for symbol in stocks:
            model_path = self.models_dir / f'{symbol}_lstm_model.h5'
            
            if not model_path.exists():
                # Model doesn't exist - needs training
                stale_stocks.append(symbol)
                logger.info(f"  {symbol}: Model not found (needs training)")
            else:
                # Check last modification time
                mod_time = datetime.fromtimestamp(model_path.stat().st_mtime)
                mod_time = self.timezone.localize(mod_time)
                
                age_days = (current_time - mod_time).days
                
                if mod_time < threshold_time:
                    stale_stocks.append(symbol)
                    logger.info(f"  {symbol}: Model stale (age: {age_days} days)")
                else:
                    logger.debug(f"  {symbol}: Model fresh (age: {age_days} days)")
        
        logger.info(f"Found {len(stale_stocks)} stale models out of {len(stocks)} stocks")
        return stale_stocks
    
    def create_training_queue(
        self,
        opportunities: List[Dict],
        max_stocks: Optional[int] = None
    ) -> List[Dict]:
        """
        Create priority-based training queue from opportunities.
        
        Args:
            opportunities: List of stock opportunities with scores
            max_stocks: Maximum number of stocks to queue (default: config value)
        
        Returns:
            List of stocks to train, sorted by priority
        """
        if max_stocks is None:
            max_stocks = self.max_models_per_night
        
        # Extract stock symbols from opportunities
        stocks = [opp.get('symbol') for opp in opportunities if opp.get('symbol')]
        
        # Check which models are stale
        stale_stocks = self.check_stale_models(stocks)
        
        # Filter opportunities to only include stale stocks
        stale_opportunities = [
            opp for opp in opportunities 
            if opp.get('symbol') in stale_stocks
        ]
        
        # Sort by opportunity score (highest first)
        if self.priority_strategy == 'highest_opportunity_score':
            sorted_opportunities = sorted(
                stale_opportunities,
                key=lambda x: x.get('opportunity_score', 0),
                reverse=True
            )
        else:
            # Default: highest score
            sorted_opportunities = sorted(
                stale_opportunities,
                key=lambda x: x.get('opportunity_score', 0),
                reverse=True
            )
        
        # Limit to max stocks
        training_queue = sorted_opportunities[:max_stocks]
        
        logger.info(f"Created training queue with {len(training_queue)} stocks")
        
        for i, opp in enumerate(training_queue[:10], 1):
            logger.info(f"  {i}. {opp.get('symbol')}: Score {opp.get('opportunity_score', 0):.1f}/100")
        
        if len(training_queue) > 10:
            logger.info(f"  ... and {len(training_queue) - 10} more stocks")
        
        return training_queue
    
    def train_stock_model(
        self,
        symbol: str,
        stock_data: Dict = None
    ) -> Dict:
        """
        Train LSTM model for a single stock.
        
        Args:
            symbol: Stock symbol
            stock_data: Stock data dictionary (optional, will fetch if not provided)
        
        Returns:
            Training results dictionary
        """
        logger.info(f"Starting LSTM training for {symbol}...")
        start_time = time.time()
        
        try:
            # Import training module (lazy import to avoid circular dependencies)
            try:
                from ..lstm.train_lstm_model import train_lstm_model
            except ImportError:
                from lstm.train_lstm_model import train_lstm_model
            
            # Train the model
            results = train_lstm_model(
                symbol=symbol,
                epochs=self.epochs,
                batch_size=self.batch_size,
                validation_split=self.validation_split,
                save_model=True
            )
            
            training_time = time.time() - start_time
            
            # Log results
            logger.info(f"✅ {symbol}: Training completed in {training_time:.1f}s")
            logger.info(f"   Loss: {results.get('final_loss', 0):.4f}")
            logger.info(f"   Val Loss: {results.get('final_val_loss', 0):.4f}")
            logger.info(f"   Accuracy: {results.get('accuracy', 0):.2f}%")
            
            # Save training log
            self._save_training_log(symbol, results, training_time)
            
            return {
                'symbol': symbol,
                'status': 'success',
                'training_time': training_time,
                'results': results
            }
        
        except Exception as e:
            training_time = time.time() - start_time
            error_msg = str(e)
            error_trace = traceback.format_exc()
            
            logger.error(f"❌ {symbol}: Training failed after {training_time:.1f}s")
            logger.error(f"   Error: {error_msg}")
            logger.debug(f"   Traceback:\n{error_trace}")
            
            return {
                'symbol': symbol,
                'status': 'failed',
                'training_time': training_time,
                'error': error_msg,
                'traceback': error_trace
            }
    
    def train_batch(
        self,
        training_queue: List[Dict],
        max_stocks: Optional[int] = None
    ) -> Dict:
        """
        Train multiple stock models in batch.
        
        Args:
            training_queue: List of stocks to train (from create_training_queue)
            max_stocks: Maximum number of stocks to train (default: config value)
        
        Returns:
            Batch training results dictionary
        """
        if not self.enabled:
            logger.info("LSTM training is disabled in configuration")
            return {
                'status': 'disabled',
                'trained_count': 0,
                'failed_count': 0,
                'total_time': 0,
                'results': []
            }
        
        if max_stocks is None:
            max_stocks = self.max_models_per_night
        
        # Limit queue size
        training_queue = training_queue[:max_stocks]
        
        logger.info("="*80)
        logger.info(f"LSTM BATCH TRAINING - {len(training_queue)} stocks")
        logger.info("="*80)
        
        batch_start_time = time.time()
        results = []
        
        for i, stock_info in enumerate(training_queue, 1):
            symbol = stock_info.get('symbol')
            logger.info(f"\n[{i}/{len(training_queue)}] Training {symbol}...")
            
            result = self.train_stock_model(symbol)
            results.append(result)
            
            # Log progress
            elapsed = time.time() - batch_start_time
            avg_time = elapsed / i
            remaining = (len(training_queue) - i) * avg_time
            
            logger.info(f"Progress: {i}/{len(training_queue)} - Elapsed: {elapsed/60:.1f}m, ETA: {remaining/60:.1f}m")
        
        total_time = time.time() - batch_start_time
        
        # Calculate statistics
        trained_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = sum(1 for r in results if r['status'] == 'failed')
        
        logger.info("="*80)
        logger.info("BATCH TRAINING COMPLETED")
        logger.info(f"  Total Time: {total_time/60:.1f} minutes")
        logger.info(f"  Trained: {trained_count}/{len(training_queue)}")
        logger.info(f"  Failed: {failed_count}/{len(training_queue)}")
        logger.info(f"  Success Rate: {trained_count/len(training_queue)*100:.1f}%")
        logger.info("="*80)
        
        return {
            'status': 'completed',
            'trained_count': trained_count,
            'failed_count': failed_count,
            'total_stocks': len(training_queue),
            'total_time': total_time,
            'results': results
        }
    
    def get_training_stats(self) -> Dict:
        """
        Get statistics about LSTM model training.
        
        Returns:
            Training statistics dictionary
        """
        stats = {
            'total_models': 0,
            'fresh_models': 0,
            'stale_models': 0,
            'missing_models': 0,
            'avg_model_age_days': 0,
            'oldest_model': None,
            'newest_model': None
        }
        
        if not self.models_dir.exists():
            return stats
        
        model_files = list(self.models_dir.glob('*_lstm_model.h5'))
        stats['total_models'] = len(model_files)
        
        if not model_files:
            return stats
        
        current_time = datetime.now(self.timezone)
        threshold_time = current_time - timedelta(days=self.stale_threshold_days)
        
        ages = []
        oldest = None
        newest = None
        
        for model_path in model_files:
            mod_time = datetime.fromtimestamp(model_path.stat().st_mtime)
            mod_time = self.timezone.localize(mod_time)
            
            age_days = (current_time - mod_time).days
            ages.append(age_days)
            
            if mod_time < threshold_time:
                stats['stale_models'] += 1
            else:
                stats['fresh_models'] += 1
            
            if oldest is None or mod_time < oldest['time']:
                oldest = {
                    'symbol': model_path.stem.replace('_lstm_model', ''),
                    'time': mod_time,
                    'age_days': age_days
                }
            
            if newest is None or mod_time > newest['time']:
                newest = {
                    'symbol': model_path.stem.replace('_lstm_model', ''),
                    'time': mod_time,
                    'age_days': age_days
                }
        
        if ages:
            stats['avg_model_age_days'] = sum(ages) / len(ages)
        
        if oldest:
            stats['oldest_model'] = {
                'symbol': oldest['symbol'],
                'age_days': oldest['age_days'],
                'last_trained': oldest['time'].strftime('%Y-%m-%d')
            }
        
        if newest:
            stats['newest_model'] = {
                'symbol': newest['symbol'],
                'age_days': newest['age_days'],
                'last_trained': newest['time'].strftime('%Y-%m-%d')
            }
        
        return stats
    
    def _save_training_log(self, symbol: str, results: Dict, training_time: float):
        """Save training log for a stock"""
        try:
            log_date = datetime.now(self.timezone).strftime('%Y-%m-%d')
            log_path = self.training_logs_dir / f'{log_date}_training_log.jsonl'
            
            log_entry = {
                'timestamp': datetime.now(self.timezone).isoformat(),
                'symbol': symbol,
                'training_time': training_time,
                'epochs': self.epochs,
                'batch_size': self.batch_size,
                'results': results
            }
            
            with open(log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        
        except Exception as e:
            logger.error(f"Failed to save training log for {symbol}: {str(e)}")


def main():
    """Command-line interface for LSTM training"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train LSTM models for stock prediction')
    parser.add_argument('--mode', choices=['check', 'train', 'stats'], default='stats',
                        help='Operation mode')
    parser.add_argument('--symbols', nargs='+', help='Stock symbols to train')
    parser.add_argument('--max-stocks', type=int, help='Maximum stocks to train')
    parser.add_argument('--force', action='store_true', help='Force training even for fresh models')
    
    args = parser.parse_args()
    
    trainer = LSTMTrainer()
    
    if args.mode == 'stats':
        # Show training statistics
        stats = trainer.get_training_stats()
        
        print("\n" + "="*80)
        print("LSTM MODEL TRAINING STATISTICS")
        print("="*80)
        print(f"Total Models: {stats['total_models']}")
        print(f"Fresh Models: {stats['fresh_models']} ({stats['fresh_models']/max(stats['total_models'], 1)*100:.1f}%)")
        print(f"Stale Models: {stats['stale_models']} ({stats['stale_models']/max(stats['total_models'], 1)*100:.1f}%)")
        print(f"Average Age: {stats['avg_model_age_days']:.1f} days")
        
        if stats.get('oldest_model'):
            print(f"\nOldest Model: {stats['oldest_model']['symbol']} ({stats['oldest_model']['age_days']} days)")
        
        if stats.get('newest_model'):
            print(f"Newest Model: {stats['newest_model']['symbol']} ({stats['newest_model']['age_days']} days)")
        
        print("="*80)
    
    elif args.mode == 'check':
        # Check for stale models
        if args.symbols:
            symbols = args.symbols
        else:
            # Load from config
            config_path = BASE_PATH / 'models' / 'config' / 'asx_sectors.json'
            with open(config_path, 'r') as f:
                sectors_config = json.load(f)
            
            symbols = []
            for sector_data in sectors_config['sectors'].values():
                symbols.extend(sector_data['stocks'])
        
        stale_stocks = trainer.check_stale_models(symbols)
        
        print(f"\nFound {len(stale_stocks)} stale models:")
        for symbol in stale_stocks[:20]:
            print(f"  - {symbol}")
        
        if len(stale_stocks) > 20:
            print(f"  ... and {len(stale_stocks) - 20} more")
    
    elif args.mode == 'train':
        # Train models
        if args.symbols:
            # Train specific symbols
            training_queue = [{'symbol': sym} for sym in args.symbols]
        else:
            # Load latest pipeline state for priority training
            state_dir = BASE_PATH / 'reports' / 'pipeline_state'
            report_date = datetime.now(trainer.timezone).strftime('%Y-%m-%d')
            state_path = state_dir / f'{report_date}_pipeline_state.json'
            
            if state_path.exists():
                with open(state_path, 'r') as f:
                    state = json.load(f)
                
                opportunities = state.get('top_opportunities', [])
                training_queue = trainer.create_training_queue(opportunities, args.max_stocks)
            else:
                print(f"Error: Pipeline state not found at {state_path}")
                print("Please run the overnight pipeline first or specify --symbols")
                return 1
        
        # Train batch
        results = trainer.train_batch(training_queue, args.max_stocks)
        
        print("\n" + "="*80)
        print("TRAINING RESULTS")
        print("="*80)
        print(f"Trained: {results['trained_count']}/{results['total_stocks']}")
        print(f"Failed: {results['failed_count']}/{results['total_stocks']}")
        print(f"Total Time: {results['total_time']/60:.1f} minutes")
        print("="*80)
        
        return 0 if results['failed_count'] == 0 else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

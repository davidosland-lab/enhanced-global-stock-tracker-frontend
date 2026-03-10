"""
Individual Stock LSTM Trainer
==============================

Interactive tool for training LSTM models for specific stocks not in the top 20.
Models are saved to the same location as overnight pipeline models.

Usage:
    python train_individual_stocks.py

Features:
- Train single or multiple stocks interactively
- Validate stock symbols (AU/US/UK markets)
- Progress tracking and logging
- Models saved to: finbert_v4.4.4/models/saved_models/
- Updates lstm_models_registry.json

Version: 1.0.0
Date: 2026-03-10
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import pytz

# Add project root to path
# Script is now inside ULTIMATE_v193_COMPLETE, so parent is the project root
BASE_PATH = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_PATH))

from pipelines.models.screening.lstm_trainer import LSTMTrainer

# Setup logging
log_dir = BASE_PATH / 'logs' / 'lstm_training'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'individual_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IndividualStockTrainer:
    """Interactive LSTM trainer for individual stocks"""
    
    def __init__(self):
        """Initialize the trainer"""
        self.trainer = LSTMTrainer()
        self.timezone = pytz.timezone('Australia/Sydney')
        
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate stock symbol format
        
        Args:
            symbol: Stock symbol (e.g., CBA.AX, AAPL, BP.L)
        
        Returns:
            True if valid format, False otherwise
        """
        symbol = symbol.strip().upper()
        
        # Check format
        if not symbol:
            return False
        
        # AU stocks should end in .AX
        if symbol.endswith('.AX'):
            return True
        
        # UK stocks should end in .L
        if symbol.endswith('.L'):
            return True
        
        # US stocks have no suffix (e.g., AAPL, GOOGL)
        if len(symbol) >= 1 and len(symbol) <= 5 and symbol.isalpha():
            return True
        
        return False
    
    def get_stock_symbols(self) -> list:
        """
        Interactively get stock symbols from user
        
        Returns:
            List of valid stock symbols
        """
        print("\n" + "="*80)
        print("INDIVIDUAL STOCK LSTM TRAINER")
        print("="*80)
        print("\nEnter stock symbols to train (one per line)")
        print("Examples:")
        print("  AU stocks: CBA.AX, BHP.AX, NAB.AX")
        print("  US stocks: AAPL, GOOGL, TSLA")
        print("  UK stocks: BP.L, HSBA.L, VOD.L")
        print("\nPress Enter on empty line when done")
        print("-"*80)
        
        symbols = []
        
        while True:
            try:
                symbol = input(f"Stock #{len(symbols)+1} (or Enter to finish): ").strip().upper()
                
                if not symbol:
                    break
                
                if self.validate_symbol(symbol):
                    if symbol not in symbols:
                        symbols.append(symbol)
                        print(f"  ✓ Added: {symbol}")
                    else:
                        print(f"  ⚠ Already in list: {symbol}")
                else:
                    print(f"  ✗ Invalid symbol format: {symbol}")
                    print(f"    Use: SYMBOL.AX (AU), SYMBOL.L (UK), or SYMBOL (US)")
                    
            except KeyboardInterrupt:
                print("\n\nTraining cancelled by user")
                sys.exit(0)
        
        return symbols
    
    def confirm_training(self, symbols: list) -> bool:
        """
        Confirm training with user
        
        Args:
            symbols: List of symbols to train
        
        Returns:
            True if confirmed, False otherwise
        """
        if not symbols:
            print("\n⚠ No stocks to train")
            return False
        
        print("\n" + "-"*80)
        print(f"READY TO TRAIN {len(symbols)} STOCK(S):")
        print("-"*80)
        
        for i, symbol in enumerate(symbols, 1):
            print(f"  {i}. {symbol}")
        
        print("-"*80)
        print(f"\nEstimated time: {len(symbols) * 3} minutes")
        print(f"Models will be saved to: finbert_v4.4.4/models/saved_models/")
        
        try:
            response = input("\nProceed with training? (yes/no): ").strip().lower()
            return response in ['yes', 'y']
        except KeyboardInterrupt:
            print("\n\nTraining cancelled by user")
            return False
    
    def train_stocks(self, symbols: list):
        """
        Train LSTM models for given symbols
        
        Args:
            symbols: List of stock symbols to train
        """
        if not symbols:
            logger.warning("No stocks to train")
            return
        
        print("\n" + "="*80)
        print("STARTING LSTM TRAINING")
        print("="*80)
        
        # Prepare stock_scores list (symbol, score) tuples
        # Use high dummy score (99.0) to ensure training
        stock_scores = [(symbol, 99.0) for symbol in symbols]
        
        logger.info(f"Training {len(symbols)} stock(s): {', '.join(symbols)}")
        
        # Train models
        start_time = datetime.now()
        
        try:
            result = self.trainer.train_priority_stocks(
                stock_scores=stock_scores,
                max_models=len(symbols)
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Display results
            print("\n" + "="*80)
            print("TRAINING COMPLETE")
            print("="*80)
            print(f"\nDuration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            print(f"Trained: {result['trained_count']} / {len(symbols)} stocks")
            print(f"Skipped: {result['skipped_count']} stocks")
            print(f"Failed: {result['failed_count']} stocks")
            
            if result['trained_stocks']:
                print("\n✓ Successfully trained:")
                for stock in result['trained_stocks']:
                    print(f"  - {stock}")
            
            if result['skipped_stocks']:
                print("\n⚠ Skipped (models already exist and not stale):")
                for stock, reason in result['skipped_stocks']:
                    print(f"  - {stock}: {reason}")
            
            if result['failed_stocks']:
                print("\n✗ Failed:")
                for stock, error in result['failed_stocks']:
                    print(f"  - {stock}: {error}")
            
            # Model locations
            print("\n" + "-"*80)
            print("MODEL FILES SAVED TO:")
            print("-"*80)
            models_dir = BASE_PATH / 'finbert_v4.4.4' / 'models' / 'saved_models'
            print(f"Directory: {models_dir}")
            
            for stock in result['trained_stocks']:
                model_file = models_dir / f'{stock}_lstm_model.h5'
                scaler_file = models_dir / f'{stock}_lstm_scaler.pkl'
                print(f"\n{stock}:")
                print(f"  Model:  {model_file.name}")
                print(f"  Scaler: {scaler_file.name}")
            
            # Registry
            registry_file = models_dir / 'lstm_models_registry.json'
            if registry_file.exists():
                print(f"\nRegistry updated: {registry_file.name}")
            
            print("\n" + "="*80)
            print("NEXT STEPS:")
            print("="*80)
            print("1. Restart the trading dashboard to load new models")
            print("2. Models will be used automatically for these stocks")
            print("3. Check logs/lstm_training/individual_training.log for details")
            
            logger.info(f"Training session complete: {result['trained_count']} trained, {result['failed_count']} failed")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            print(f"\n✗ ERROR: Training failed - {e}")
            print(f"Check logs: {log_dir / 'individual_training.log'}")
    
    def run(self):
        """Main interactive training loop"""
        try:
            # Get symbols from user
            symbols = self.get_stock_symbols()
            
            # Confirm and train
            if self.confirm_training(symbols):
                self.train_stocks(symbols)
            else:
                print("\nTraining cancelled")
                
        except Exception as e:
            logger.error(f"Error in training session: {e}")
            print(f"\n✗ ERROR: {e}")
            print(f"Check logs: {log_dir / 'individual_training.log'}")


def main():
    """Main entry point"""
    trainer = IndividualStockTrainer()
    trainer.run()


if __name__ == "__main__":
    main()

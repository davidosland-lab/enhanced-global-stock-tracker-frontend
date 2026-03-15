#!/usr/bin/env python3
"""
Train LSTM Models for Australian (ASX) Stocks
FinBERT v4.0 - Specialized for ASX symbols
"""

import sys
import os
import argparse
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.train_lstm import train_model_for_symbol, train_multiple_symbols

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Common Australian stocks with proper Yahoo Finance symbols
ASX_STOCKS = {
    'CBA': 'CBA.AX',   # Commonwealth Bank
    'BHP': 'BHP.AX',   # BHP Group
    'CSL': 'CSL.AX',   # CSL Limited
    'WBC': 'WBC.AX',   # Westpac
    'ANZ': 'ANZ.AX',   # ANZ Bank
    'NAB': 'NAB.AX',   # National Australia Bank
    'WES': 'WES.AX',   # Wesfarmers
    'MQG': 'MQG.AX',   # Macquarie Group
    'TLS': 'TLS.AX',   # Telstra
    'WOW': 'WOW.AX',   # Woolworths
    'RIO': 'RIO.AX',   # Rio Tinto
    'FMG': 'FMG.AX',   # Fortescue Metals
    'NCM': 'NCM.AX',   # Newcrest Mining
    'STO': 'STO.AX',   # Santos
    'WPL': 'WPL.AX',   # Woodside Petroleum
    'ALL': 'ALL.AX',   # Aristocrat Leisure
    'GMG': 'GMG.AX',   # Goodman Group
    'TCL': 'TCL.AX',   # Transurban
    'REA': 'REA.AX',   # REA Group
    'COL': 'COL.AX',   # Coles Group
}

def format_asx_symbol(symbol: str) -> str:
    """
    Format ASX symbol correctly for Yahoo Finance
    
    Args:
        symbol: Raw symbol (e.g., 'CBA' or 'CBA.AX')
    
    Returns:
        Properly formatted symbol with .AX suffix
    """
    symbol = symbol.upper().strip()
    
    # If already has .AX, return as is
    if symbol.endswith('.AX'):
        return symbol
    
    # If it's a known ASX stock without suffix, add it
    if symbol in ASX_STOCKS:
        return ASX_STOCKS[symbol]
    
    # Otherwise, assume it's ASX and add suffix
    return f"{symbol}.AX"

def main():
    parser = argparse.ArgumentParser(description='Train LSTM models for Australian stocks')
    parser.add_argument('--symbol', type=str, help='Single ASX symbol (e.g., CBA or CBA.AX)')
    parser.add_argument('--symbols', type=str, help='Comma-separated ASX symbols')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--top4banks', action='store_true', help='Train Big 4 Australian banks')
    parser.add_argument('--top10', action='store_true', help='Train top 10 ASX stocks')
    parser.add_argument('--miners', action='store_true', help='Train mining stocks')
    
    args = parser.parse_args()
    
    # Determine which symbols to train
    symbols = []
    
    if args.top4banks:
        symbols = ['CBA.AX', 'WBC.AX', 'ANZ.AX', 'NAB.AX']
        logger.info("Training Big 4 Australian Banks")
    elif args.top10:
        symbols = ['CBA.AX', 'BHP.AX', 'CSL.AX', 'WBC.AX', 'ANZ.AX', 
                  'NAB.AX', 'WES.AX', 'MQG.AX', 'TLS.AX', 'WOW.AX']
        logger.info("Training Top 10 ASX Stocks")
    elif args.miners:
        symbols = ['BHP.AX', 'RIO.AX', 'FMG.AX', 'NCM.AX', 'STO.AX']
        logger.info("Training Mining Stocks")
    elif args.symbols:
        # Multiple symbols provided
        raw_symbols = args.symbols.split(',')
        symbols = [format_asx_symbol(s) for s in raw_symbols]
    elif args.symbol:
        # Single symbol provided
        symbols = [format_asx_symbol(args.symbol)]
    else:
        # Default: Train CBA as example
        symbols = ['CBA.AX']
        logger.info("No symbol specified, training CBA.AX as example")
    
    logger.info(f"Training LSTM models for: {symbols}")
    logger.info(f"Epochs: {args.epochs}")
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Train the models
    if len(symbols) == 1:
        result = train_model_for_symbol(symbols[0], epochs=args.epochs)
        
        print("\n" + "="*60)
        print("TRAINING COMPLETE")
        print("="*60)
        print(f"\nSymbol: {symbols[0]}")
        
        if 'error' not in result:
            print(f"Status: {result.get('status', 'Unknown')}")
            if 'training_results' in result:
                train_res = result['training_results']
                print(f"Final Loss: {train_res.get('final_loss', 'N/A'):.4f}")
                print(f"Final Val Loss: {train_res.get('final_val_loss', 'N/A'):.4f}")
            if 'test_prediction' in result:
                pred = result['test_prediction']
                print(f"Test Prediction: {pred.get('prediction')} ({pred.get('confidence')}% confidence)")
                print(f"Current Price: ${pred.get('current_price', 0):.2f}")
                print(f"Predicted Price: ${pred.get('predicted_price', 0):.2f}")
        else:
            print(f"ERROR: {result['error']}")
    else:
        results = train_multiple_symbols(symbols, epochs=args.epochs)
        
        print("\n" + "="*60)
        print("TRAINING SUMMARY - AUSTRALIAN STOCKS")
        print("="*60)
        
        for symbol, result in results.items():
            stock_name = symbol
            for name, sym in ASX_STOCKS.items():
                if sym == symbol:
                    stock_name = f"{symbol} ({name})"
                    break
            
            print(f"\n{stock_name}:")
            
            if 'error' not in result:
                print(f"  Status: {result.get('status', 'Unknown')}")
                if 'training_results' in result:
                    train_res = result['training_results']
                    print(f"  Final Loss: {train_res.get('final_loss', 'N/A'):.4f}")
                    print(f"  Val Loss: {train_res.get('final_val_loss', 'N/A'):.4f}")
                if 'test_prediction' in result:
                    pred = result['test_prediction']
                    print(f"  Prediction: {pred.get('prediction')} ({pred.get('confidence'):.1f}%)")
                    print(f"  Current: ${pred.get('current_price', 0):.2f} AUD")
                    print(f"  Target: ${pred.get('predicted_price', 0):.2f} AUD")
            else:
                print(f"  ERROR: {result['error']}")
    
    print("\n" + "="*60)
    print("Australian stock training complete!")
    print("Models saved to: models/")

if __name__ == "__main__":
    main()
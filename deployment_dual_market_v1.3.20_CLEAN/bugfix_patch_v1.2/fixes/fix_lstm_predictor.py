"""
Bug Fix Patch v1.2 - Fix lstm_predictor.py
FinBERT v4.4.4
Removes ALL mock sentiment references
"""

import sys
import os
import shutil
from datetime import datetime

def apply_fix(finbert_path):
    """Apply lstm_predictor.py fixes"""
    
    print("\n" + "="*60)
    print("Fixing lstm_predictor.py - Removing Mock Sentiment")
    print("="*60)
    
    lstm_file = os.path.join(finbert_path, 'finbert_v4.4.4', 'models', 'lstm_predictor.py')
    
    if not os.path.exists(lstm_file):
        print("ERROR: lstm_predictor.py not found at:", lstm_file)
        return False
    
    # Backup
    backup_path = lstm_file + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy2(lstm_file, backup_path)
    print(f"[OK] Created backup: {backup_path}")
    
    # Read file
    try:
        with open(lstm_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(lstm_file, 'r', encoding='latin-1') as f:
            content = f.read()
    
    # Count changes
    changes = 0
    
    # Fix 1: Remove mock sentiment from _get_sentiment method
    old_code_1 = '''    def _get_sentiment(self, symbol: str) -> Optional[Dict]:
        """Get sentiment data for a symbol"""
        if FINBERT_AVAILABLE and finbert_analyzer:
            return finbert_analyzer.get_mock_sentiment(symbol)
        return None'''
    
    new_code_1 = '''    def _get_sentiment(self, symbol: str) -> Optional[Dict]:
        """
        Get REAL sentiment data for a symbol
        NO MOCK/FAKE/SYNTHETIC DATA - Returns None if real sentiment unavailable
        """
        # NO MOCK DATA - sentiment must come from real FinBERT analysis
        # This will be populated by the API layer with real sentiment
        return None'''
    
    if old_code_1 in content:
        content = content.replace(old_code_1, new_code_1)
        changes += 1
        print("[OK] Removed mock sentiment from _get_sentiment()")
    
    # Write fixed file
    with open(lstm_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n[OK] Applied {changes} fix(es) to lstm_predictor.py")
    print("[OK] File now uses REAL data only")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_lstm_predictor.py <path_to_finbert>")
        print("Example: python fix_lstm_predictor.py C:\\Users\\david\\AATelS")
        sys.exit(1)
    
    finbert_path = sys.argv[1]
    success = apply_fix(finbert_path)
    sys.exit(0 if success else 1)

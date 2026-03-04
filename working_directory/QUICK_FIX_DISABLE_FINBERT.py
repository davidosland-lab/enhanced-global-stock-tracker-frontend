"""
QUICK FIX: Disable FinBERT to stop download loop
Automatically patches sentiment_integration.py to disable FinBERT

Run this script from: C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
Usage: python QUICK_FIX_DISABLE_FINBERT.py
"""

import os
import shutil
from pathlib import Path

def apply_quick_fix():
    """Apply quick fix to disable FinBERT"""
    
    # Find sentiment_integration.py
    current_dir = Path.cwd()
    target_file = current_dir / 'sentiment_integration.py'
    
    if not target_file.exists():
        print("❌ ERROR: sentiment_integration.py not found")
        print(f"Expected location: {target_file}")
        print(f"Current directory: {current_dir}")
        print("\nMake sure you're running this from:")
        print("C:\\Users\\david\\Regime_trading\\COMPLETE_SYSTEM_v1.3.15.45_FINAL")
        return False
    
    print("=" * 60)
    print("QUICK FIX: Disable FinBERT Download Loop")
    print("=" * 60)
    print()
    print(f"Target file: {target_file}")
    print()
    
    # Create backup
    backup_file = target_file.with_suffix('.py.backup')
    shutil.copy2(target_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    print()
    
    # Read original file
    with open(target_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the line to modify (around line 88)
    modified = False
    new_lines = []
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Find the line: self.finbert_analyzer = FinBERTSentimentAnalyzer(model_name="ProsusAI/finbert")
        if 'self.finbert_analyzer = FinBERTSentimentAnalyzer(model_name="ProsusAI/finbert")' in line:
            print(f"Found target at line {line_num}")
            print(f"Original: {line.strip()}")
            
            # Replace with commented version + disable
            new_lines.append('                # TEMPORARY FIX: Disable FinBERT to prevent HuggingFace download loop\n')
            new_lines.append('                # ' + line)  # Comment original line
            new_lines.append('                self.finbert_analyzer = None\n')
            new_lines.append('                self.use_finbert = False\n')
            new_lines.append('                logger.info("[SENTIMENT] FinBERT DISABLED - using keyword-based sentiment only")\n')
            
            modified = True
            print(f"✅ Modified: FinBERT disabled")
            print()
        else:
            new_lines.append(line)
    
    if not modified:
        print("⚠️  WARNING: Could not find target line")
        print("The file may have been modified already")
        print("Searching for alternative pattern...")
        
        # Try alternative search
        for i, line in enumerate(lines):
            if 'FinBERTSentimentAnalyzer' in line and 'self.finbert_analyzer' in line:
                print(f"Found similar pattern at line {i+1}: {line.strip()}")
        
        return False
    
    # Write modified file
    with open(target_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("=" * 60)
    print("✅ FIX APPLIED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("What changed:")
    print("  • FinBERT initialization is now DISABLED")
    print("  • System will use keyword-based sentiment (fast)")
    print("  • No more HuggingFace downloads")
    print("  • Dashboard will start in 10-15 seconds")
    print()
    print("Backup saved to:")
    print(f"  {backup_file}")
    print()
    print("To restore original:")
    print(f"  copy {backup_file.name} sentiment_integration.py")
    print()
    print("=" * 60)
    print("NEXT STEP: Restart the dashboard")
    print("=" * 60)
    print()
    print("  python unified_trading_dashboard.py")
    print()
    print("Expected result:")
    print("  ✅ Dashboard starts in 10-15 seconds")
    print("  ✅ No 'Downloading...' messages")
    print("  ✅ Market data loads normally")
    print("  ✅ Trading signals work")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = apply_quick_fix()
        
        if success:
            print("🎉 Ready to restart dashboard!")
        else:
            print("❌ Fix could not be applied")
            print("Please check the error messages above")
        
        input("\nPress Enter to exit...")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nIf you need help, the manual fix is:")
        print("1. Open: sentiment_integration.py")
        print("2. Find line ~88: self.finbert_analyzer = FinBERTSentimentAnalyzer(...)")
        print("3. Comment it out and add:")
        print("   self.finbert_analyzer = None")
        print("   self.use_finbert = False")
        print("   logger.info('[SENTIMENT] FinBERT DISABLED - using keyword-based sentiment only')")
        
        input("\nPress Enter to exit...")

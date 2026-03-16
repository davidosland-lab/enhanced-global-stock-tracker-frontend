"""
Check if train_lstm.py passes symbol to predictor
"""

from pathlib import Path

print("\n" + "="*70)
print("CHECKING train_lstm.py")
print("="*70)

train_file = Path("finbert_v4.4.4/models/train_lstm.py")

if not train_file.exists():
    print("ERROR: File not found!")
    exit(1)

content = train_file.read_text(encoding='utf-8', errors='ignore')
lines = content.split('\n')

# Find StockLSTMPredictor initialization
print("\n[1] LOOKING FOR StockLSTMPredictor INITIALIZATION:")
print("-" * 70)

found = False
for i, line in enumerate(lines):
    if 'StockLSTMPredictor(' in line:
        # Show context (10 lines before and after)
        start = max(0, i - 3)
        end = min(len(lines), i + 10)
        
        print(f"\nFound at line {i+1}:")
        for j in range(start, end):
            marker = " >>> " if j == i else "     "
            print(f"{marker}{j+1:4d}: {lines[j]}")
        found = True

if not found:
    print("❌ Could not find StockLSTMPredictor initialization!")

# Check if symbol is passed
print("\n" + "="*70)
print("KEY CHECK:")
print("="*70)

passes_symbol = "symbol=symbol" in content and "StockLSTMPredictor" in content

print(f"\n✓ or ✗: Passes 'symbol=symbol' to StockLSTMPredictor? {passes_symbol}")

if passes_symbol:
    print("\n✅ CORRECT! train_lstm.py passes symbol to predictor")
else:
    print("\n❌ PROBLEM! train_lstm.py does NOT pass symbol to predictor")
    print("\nIt should look like:")
    print("""
    predictor = StockLSTMPredictor(
        sequence_length=sequence_length,
        features=available_features,
        symbol=symbol  # ← This line is needed!
    )
    """)

print("\n" + "="*70)

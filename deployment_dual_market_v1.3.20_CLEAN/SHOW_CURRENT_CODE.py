"""
Show exactly what code is in your current lstm_predictor.py file
"""

from pathlib import Path

print("\n" + "="*70)
print("SHOWING YOUR CURRENT CODE")
print("="*70)

lstm_file = Path("finbert_v4.4.4/models/lstm_predictor.py")

if not lstm_file.exists():
    print("ERROR: File not found!")
    exit(1)

content = lstm_file.read_text(encoding='utf-8', errors='ignore')

# Show __init__ method
print("\n[1] YOUR __init__ METHOD:")
print("-" * 70)
lines = content.split('\n')
in_init = False
init_lines = []
indent_count = 0

for i, line in enumerate(lines):
    if 'def __init__(self' in line and 'StockLSTMPredictor' in content[max(0, content.find(line)-500):content.find(line)]:
        in_init = True
        indent_count = 0
    
    if in_init:
        init_lines.append(f"{i+1:4d}: {line}")
        if line.strip() and not line.strip().startswith('#'):
            if indent_count == 0:
                indent_count = len(line) - len(line.lstrip())
            elif line.strip() and len(line) - len(line.lstrip()) <= indent_count and 'def __init__' not in line:
                break

for line in init_lines[:30]:  # Show first 30 lines
    print(line)

# Show model_path assignment
print("\n[2] YOUR model_path ASSIGNMENT:")
print("-" * 70)
for i, line in enumerate(lines):
    if 'self.model_path' in line and '=' in line:
        print(f"{i+1:4d}: {line}")

# Show save_model method
print("\n[3] YOUR save_model METHOD (first part):")
print("-" * 70)
in_save = False
save_lines = []

for i, line in enumerate(lines):
    if 'def save_model(self' in line:
        in_save = True
    
    if in_save:
        save_lines.append(f"{i+1:4d}: {line}")
        if len(save_lines) > 25:  # Show first 25 lines
            break

for line in save_lines:
    print(line)

# Key checks
print("\n" + "="*70)
print("KEY CHECKS:")
print("="*70)

has_symbol_param = "symbol: str = None" in content
has_symbol_path = "f'models/{symbol}_lstm_model.keras'" in content or 'f"models/{symbol}_lstm_model.keras"' in content
has_format_string = "{symbol}" in content and "model_path" in content

print(f"\n1. Has 'symbol: str = None' parameter? {has_symbol_param}")
print(f"2. Has symbol-specific f-string path? {has_symbol_path}")
print(f"3. Has any {{symbol}} formatting? {has_format_string}")

if not has_symbol_param:
    print("\n❌ PROBLEM: Missing 'symbol' parameter in __init__")
    print("   Your __init__ should look like:")
    print("   def __init__(self, sequence_length: int = 60, features: List[str] = None, symbol: str = None):")

if not has_symbol_path:
    print("\n❌ PROBLEM: Not using symbol-specific path")
    print("   Your code should have:")
    print("   self.model_path = f'models/{symbol}_lstm_model.keras'")

print("\n" + "="*70)

#!/usr/bin/env python3
import os, sys, shutil
from datetime import datetime

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

base_path = sys.argv[1] if len(sys.argv) > 1 else input("Enter FinBERT path: ").strip()
config_file = os.path.join(base_path, 'finbert_v4.4.4', 'config_dev.py')

if not os.path.exists(config_file):
    print("[INFO] No config_dev.py found (optional)")
    sys.exit(0)

print(f"[OK] Found: {config_file}")

# Backup
backup = f"{config_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(config_file, backup)
print(f"[OK] Backup: {backup}")

# Read and update
with open(config_file, 'r') as f:
    content = f.read()

if 'USE_LSTM' in content:
    import re
    content = re.sub(r"'USE_LSTM':\s*True", "'USE_LSTM': False  # Disabled by patch", content)
    print("[OK] Updated USE_LSTM to False")
else:
    content += "\n\nFEATURES = {'USE_LSTM': False}  # Patch v1.1\n"
    print("[OK] Added FEATURES config")

with open(config_file, 'w') as f:
    f.write(content)

print("[OK] Config updated")

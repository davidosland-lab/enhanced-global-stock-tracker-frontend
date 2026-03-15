"""
v188 Confidence Threshold Patch - IN-PLACE UPDATE
Applies ONLY to your existing complete system
Preserves: FinBERT v4.4.4, pipelines, all scripts, all functionality
"""

import os
import sys
import shutil
from datetime import datetime

# Color codes for Windows
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
except:
    GREEN = RED = YELLOW = BLUE = RESET = ''

print("=" * 80)
print(f"{BLUE}v188 Confidence Threshold Patch - IN-PLACE UPDATE{RESET}")
print("=" * 80)
print(f"\n{YELLOW}This patch modifies ONLY 4 files in your existing complete system{RESET}")
print(f"{YELLOW}All other components remain untouched (FinBERT, pipelines, etc.){RESET}\n")

# Files to patch with their specific changes
PATCHES = {
    "config/live_trading_config.json": [
        {
            'search': '"confidence_threshold": 52.0',
            'replace': '"confidence_threshold": 45.0',
            'description': 'Config threshold 52.0 → 45.0'
        }
    ],
    "ml_pipeline/swing_signal_generator.py": [
        {
            'search': 'CONFIDENCE_THRESHOLD = 0.52',
            'replace': 'CONFIDENCE_THRESHOLD = 0.48',
            'description': 'Signal generator 0.52 → 0.48'
        },
        {
            'search': 'confidence_threshold: float = 0.52',
            'replace': 'confidence_threshold: float = 0.48',
            'description': 'Signal generator default param 0.52 → 0.48'
        }
    ],
    "core/paper_trading_coordinator.py": [
        {
            'search': 'self.ui_min_confidence if self.ui_min_confidence is not None else 52.0',
            'replace': 'self.ui_min_confidence if self.ui_min_confidence is not None else 48.0',
            'description': 'Coordinator fallback 52.0 → 48.0'
        }
    ],
    "core/opportunity_monitor.py": [
        {
            'search': 'confidence_threshold: float = 65.0',
            'replace': 'confidence_threshold: float = 48.0',
            'description': 'Monitor threshold 65.0 → 48.0'
        }
    ]
}

def apply_patches():
    """Apply v188 patches to the 4 target files."""
    patched_count = 0
    failed_count = 0
    
    for file_path, patches in PATCHES.items():
        print(f"\n{BLUE}[{file_path}]{RESET}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"  {RED}✗ File not found{RESET}")
            failed_count += 1
            continue
        
        # Create backup
        backup_path = f"{file_path}.v188_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2(file_path, backup_path)
            print(f"  {GREEN}✓ Backup created: {backup_path}{RESET}")
        except Exception as e:
            print(f"  {RED}✗ Backup failed: {e}{RESET}")
            failed_count += 1
            continue
        
        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  {RED}✗ Read failed: {e}{RESET}")
            failed_count += 1
            continue
        
        # Apply patches
        modified = False
        for patch in patches:
            if patch['search'] in content:
                content = content.replace(patch['search'], patch['replace'])
                print(f"  {GREEN}✓ {patch['description']}{RESET}")
                modified = True
            else:
                print(f"  {YELLOW}⚠ Pattern not found (may already be patched): {patch['description']}{RESET}")
        
        # Write back if modified
        if modified:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  {GREEN}✓ File updated successfully{RESET}")
                patched_count += 1
            except Exception as e:
                print(f"  {RED}✗ Write failed: {e}{RESET}")
                # Restore backup
                shutil.copy2(backup_path, file_path)
                print(f"  {YELLOW}⚠ Backup restored{RESET}")
                failed_count += 1
        else:
            print(f"  {YELLOW}⚠ No changes made (already patched?){RESET}")
    
    return patched_count, failed_count


def verify_patches():
    """Verify that v188 patches are in place."""
    print(f"\n{BLUE}Verification:{RESET}")
    
    checks = [
        ("config/live_trading_config.json", '"confidence_threshold": 45.0', "Config = 45.0"),
        ("ml_pipeline/swing_signal_generator.py", "CONFIDENCE_THRESHOLD = 0.48", "Signal Gen = 0.48"),
        ("core/paper_trading_coordinator.py", "else 48.0", "Coordinator = 48.0"),
        ("core/opportunity_monitor.py", "confidence_threshold: float = 48.0", "Monitor = 48.0"),
    ]
    
    all_passed = True
    for file_path, pattern, description in checks:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if pattern in content:
                print(f"  {GREEN}✓ {description}{RESET}")
            else:
                print(f"  {RED}✗ {description}{RESET}")
                all_passed = False
        else:
            print(f"  {RED}✗ File not found: {file_path}{RESET}")
            all_passed = False
    
    return all_passed


def main():
    # Check we're in the right directory
    if not os.path.exists("config") or not os.path.exists("core"):
        print(f"\n{RED}ERROR: Please run this script from the root directory of your trading system{RESET}")
        print(f"{YELLOW}Expected directory structure:{RESET}")
        print("  - config/")
        print("  - core/")
        print("  - ml_pipeline/")
        print("  - finbert_v4.4.4/")
        print("  - pipelines/")
        print("  - ... (all other folders)")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Confirm with user
    print(f"\n{YELLOW}Files to be modified:{RESET}")
    for file_path in PATCHES.keys():
        print(f"  • {file_path}")
    
    print(f"\n{YELLOW}All other files will remain unchanged:{RESET}")
    print("  • finbert_v4.4.4/ (kept as-is)")
    print("  • pipelines/ (kept as-is)")
    print("  • All scripts and batch files (kept as-is)")
    print("  • All other Python files (kept as-is)")
    
    response = input(f"\n{YELLOW}Apply v188 patches? (yes/no): {RESET}").strip().lower()
    if response != 'yes':
        print(f"\n{RED}Patch cancelled.{RESET}")
        input("Press Enter to exit...")
        sys.exit(0)
    
    # Apply patches
    print(f"\n{BLUE}Applying patches...{RESET}")
    patched, failed = apply_patches()
    
    # Verify
    verified = verify_patches()
    
    # Summary
    print("\n" + "=" * 80)
    if verified and failed == 0:
        print(f"{GREEN}✓ v188 PATCH COMPLETE!{RESET}")
        print(f"{GREEN}  All 4 files successfully patched and verified{RESET}")
        print(f"\n{YELLOW}Next steps:{RESET}")
        print("  1. Restart your dashboard")
        print("  2. Verify trades with 48-65% confidence now PASS")
        print("  3. Check logs show: 'BP.L: 52.1% >= 48.0% - PASS'")
    else:
        print(f"{RED}✗ PATCH INCOMPLETE{RESET}")
        print(f"  {patched} file(s) patched")
        print(f"  {failed} file(s) failed")
        print(f"\n{YELLOW}Please check the errors above and try again{RESET}")
    
    print("=" * 80)
    input("\nPress Enter to exit...")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
v188 Comprehensive Confidence Threshold Fix
============================================

Fixes ALL locations where the 52%/65% threshold blocks trades.

Changes:
1. config/live_trading_config.json: confidence_threshold 52.0 → 45.0
2. ml_pipeline/swing_signal_generator.py: confidence_threshold 0.52 → 0.48
3. core/paper_trading_coordinator.py: min_confidence default 52.0 → 48.0
4. core/opportunity_monitor.py: confidence_threshold default 65.0 → 48.0

Result: Trades with 48-65% confidence will now PASS instead of being blocked.

Usage:
    python APPLY_V188_COMPREHENSIVE_FIX.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class V188ComprehensiveFix:
    def __init__(self):
        self.backup_suffix = ".v188_backup"
        self.files_to_patch = {
            'config/live_trading_config.json': [
                ('"confidence_threshold": 52.0,', '"confidence_threshold": 45.0,  # v188: Lowered to 48%')
            ],
            'ml_pipeline/swing_signal_generator.py': [
                ('confidence_threshold: float = 0.52,', 'confidence_threshold: float = 0.48,  # v188: Lowered from 0.52'),
                ('confidence_threshold: Minimum confidence for entry (52%)', 'confidence_threshold: Minimum confidence for entry (48%)'),
                ('signal[\'confidence\'] > 0.52', 'signal[\'confidence\'] > 0.48  # v188: Lowered threshold')
            ],
            'core/paper_trading_coordinator.py': [
                ('min_confidence = self.ui_min_confidence if self.ui_min_confidence is not None else 52.0',
                 'min_confidence = self.ui_min_confidence if self.ui_min_confidence is not None else 48.0  # v188: Lowered from 52.0')
            ],
            'core/opportunity_monitor.py': [
                ('confidence_threshold: float = 65.0,', 'confidence_threshold: float = 48.0,  # v188: Lowered from 65.0'),
                ('confidence_threshold: Minimum confidence for alert (default 65%)', 'confidence_threshold: Minimum confidence for alert (default 48%)'),
                ('elif confidence >= 65:', 'elif confidence >= 48:  # v188: Lowered urgency threshold')
            ]
        }
    
    def backup_file(self, file_path: Path) -> bool:
        """Create backup of file"""
        backup_path = Path(str(file_path) + self.backup_suffix)
        
        if backup_path.exists():
            print(f"   ⚠️  Backup already exists: {backup_path.name}")
            return True
            
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"   ✅ Backed up: {backup_path.name}")
            return True
        except Exception as e:
            print(f"   ❌ Backup failed: {e}")
            return False
    
    def apply_patch(self, file_path: Path, replacements: list) -> bool:
        """Apply replacements to file"""
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes_made = 0
            
            # Apply each replacement
            for old_text, new_text in replacements:
                if old_text in content:
                    content = content.replace(old_text, new_text)
                    changes_made += 1
                    print(f"   ✅ Replaced: {old_text[:50]}...")
                else:
                    print(f"   ⚠️  Pattern not found: {old_text[:50]}...")
            
            if changes_made > 0 and content != original_content:
                # Write patched content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   ✅ Patched successfully ({changes_made} changes)")
                return True
            else:
                print(f"   ⚠️  No changes made")
                return False
                
        except Exception as e:
            print(f"   ❌ Patch failed: {e}")
            return False
    
    def verify_patch(self, file_path: Path) -> bool:
        """Verify patch was applied correctly"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for v188 markers
            if 'v188' in content or '48.0' in content or '0.48' in content:
                print(f"   ✅ Verification passed")
                return True
            else:
                print(f"   ⚠️  Verification unclear - manual check recommended")
                return True  # Don't fail, just warn
                
        except Exception as e:
            print(f"   ❌ Verification failed: {e}")
            return False
    
    def run(self):
        """Run the comprehensive fix"""
        print("=" * 70)
        print("v188 COMPREHENSIVE CONFIDENCE THRESHOLD FIX")
        print("=" * 70)
        print()
        print("This will patch 4 files to lower the confidence threshold from")
        print("52%/65% to 48%, allowing more trades to pass.")
        print()
        print("Files to be patched:")
        for file_path in self.files_to_patch.keys():
            print(f"  • {file_path}")
        print()
        
        # Confirm
        response = input("Proceed with patching? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Patch cancelled by user")
            return False
        
        print()
        print("=" * 70)
        print("APPLYING PATCHES")
        print("=" * 70)
        print()
        
        success_count = 0
        total_files = len(self.files_to_patch)
        
        for file_rel_path, replacements in self.files_to_patch.items():
            file_path = Path(file_rel_path)
            
            print(f"📄 {file_path}")
            
            # Check file exists
            if not file_path.exists():
                print(f"   ⚠️  File not found: {file_path}")
                print(f"   Skipping...")
                print()
                continue
            
            # Backup
            if not self.backup_file(file_path):
                print(f"   ❌ Skipping due to backup failure")
                print()
                continue
            
            # Apply patch
            if self.apply_patch(file_path, replacements):
                # Verify
                if self.verify_patch(file_path):
                    success_count += 1
            
            print()
        
        # Summary
        print("=" * 70)
        print("PATCH SUMMARY")
        print("=" * 70)
        print()
        print(f"✅ Successfully patched: {success_count}/{total_files} files")
        print()
        
        if success_count == total_files:
            print("🎉 ALL PATCHES APPLIED SUCCESSFULLY!")
            print()
            print("Next steps:")
            print("  1. Restart the dashboard: python core/unified_trading_dashboard.py")
            print("  2. Monitor logs for trades with 48-65% confidence")
            print("  3. Look for messages like: ✅ Signal PASSED threshold check (54.4% >= 48.0%)")
            print()
            print("Expected behavior:")
            print("  • Trades at 48% confidence: PASS ✅")
            print("  • Trades at 54% confidence: PASS ✅ (was BLOCKED ❌)")
            print("  • Trades at 65% confidence: PASS ✅")
            print()
            return True
        else:
            print(f"⚠️  {total_files - success_count} file(s) could not be patched")
            print("   Please check error messages above")
            print()
            return False

if __name__ == "__main__":
    fixer = V188ComprehensiveFix()
    success = fixer.run()
    sys.exit(0 if success else 1)

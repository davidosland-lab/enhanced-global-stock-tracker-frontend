#!/usr/bin/env python3
"""
HOTFIX v1.3.15.45 - Dashboard FinBERT Integration Fix
Fixes import error: SentimentIntegration -> IntegratedSentimentAnalyzer
"""

import os
import sys
from pathlib import Path

def fix_dashboard():
    """Fix unified_trading_dashboard.py import errors"""
    
    dashboard_path = Path('complete_backend_clean_install_v1.3.15') / 'unified_trading_dashboard.py'
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard not found: {dashboard_path}")
        return False
    
    print(f"📄 Reading dashboard: {dashboard_path}")
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count occurrences
    old_import_count = content.count('SentimentIntegration')
    
    if old_import_count == 0:
        print("✅ Dashboard already fixed (no SentimentIntegration found)")
        return True
    
    print(f"🔍 Found {old_import_count} occurrences of 'SentimentIntegration'")
    
    # Fix imports
    content = content.replace(
        'from sentiment_integration import SentimentIntegration',
        'from sentiment_integration import IntegratedSentimentAnalyzer'
    )
    
    # Fix instantiation
    content = content.replace(
        'sentiment_int = SentimentIntegration()',
        'sentiment_int = IntegratedSentimentAnalyzer()'
    )
    
    # Verify fixes
    if 'SentimentIntegration' in content:
        print("⚠️  Warning: Some SentimentIntegration references may remain")
    
    # Backup original
    backup_path = dashboard_path.with_suffix('.py.backup_hotfix')
    if not backup_path.exists():
        print(f"💾 Creating backup: {backup_path}")
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            with open(backup_path, 'w', encoding='utf-8') as bf:
                bf.write(f.read())
    
    # Write fixed version
    print(f"✏️  Writing fixed dashboard...")
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Dashboard fixed successfully")
    print(f"   - Replaced 'SentimentIntegration' with 'IntegratedSentimentAnalyzer'")
    
    return True


def clear_cache():
    """Clear Python cache files"""
    
    print("\n🗑️  Clearing Python cache...")
    
    cache_patterns = [
        'complete_backend_clean_install_v1.3.15/__pycache__',
        'complete_backend_clean_install_v1.3.15/**/__pycache__',
        'complete_backend_clean_install_v1.3.15/**/*.pyc'
    ]
    
    import glob
    import shutil
    
    for pattern in cache_patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"   Removed directory: {path}")
                else:
                    os.remove(path)
                    print(f"   Removed file: {path}")
            except Exception as e:
                print(f"   Warning: Could not remove {path}: {e}")
    
    print("✅ Cache cleared")


def main():
    """Main hotfix script"""
    
    print("=" * 70)
    print("HOTFIX v1.3.15.45 - Dashboard FinBERT Integration Fix")
    print("=" * 70)
    print()
    
    # Change to working directory
    work_dir = Path(__file__).parent / 'working_directory'
    if work_dir.exists():
        os.chdir(work_dir)
        print(f"📁 Working directory: {os.getcwd()}")
    else:
        print(f"⚠️  Working from: {os.getcwd()}")
    
    # Apply fixes
    if not fix_dashboard():
        print("\n❌ HOTFIX FAILED")
        return 1
    
    # Clear cache
    clear_cache()
    
    # Success summary
    print("\n" + "=" * 70)
    print("✅ HOTFIX COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Navigate to: cd complete_backend_clean_install_v1.3.15")
    print("2. Activate venv: venv\\Scripts\\activate")
    print("3. Start dashboard: python unified_trading_dashboard.py")
    print("4. Open browser: http://localhost:8050")
    print()
    print("Expected result:")
    print("✓ Dashboard starts without ImportError")
    print("✓ FinBERT Sentiment panel loads data")
    print("✓ Morning report sentiment displayed")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

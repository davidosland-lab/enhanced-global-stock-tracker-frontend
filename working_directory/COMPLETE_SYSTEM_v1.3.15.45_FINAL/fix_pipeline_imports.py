"""
Fix Pipeline Import Paths and Emoji Encoding Issues
====================================================

This script fixes two critical issues in pipeline runners:
1. Import path issue (parent.parent -> parent)
2. Windows console emoji encoding errors

Run this once to fix all pipeline files.
"""

import re
from pathlib import Path

def fix_pipeline_file(filepath):
    """Fix import paths and emoji encoding in a pipeline file"""
    print(f"\nFixing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix 1: Change parent.parent to parent for imports
    content = content.replace(
        "sys.path.insert(0, str(Path(__file__).parent.parent))",
        "sys.path.insert(0, str(Path(__file__).parent))"
    )
    
    # Fix 2: Add better error handling for imports
    old_import = """try:
    from paper_trading_coordinator import PaperTradingCoordinator
    from ml_pipeline.market_calendar import MarketCalendar, Exchange, MarketStatus
except ImportError:
    PaperTradingCoordinator = None
    MarketCalendar = None
    Exchange = None
    MarketStatus = None"""
    
    new_import = """try:
    from paper_trading_coordinator import PaperTradingCoordinator
    from ml_pipeline.market_calendar import MarketCalendar, Exchange, MarketStatus
except ImportError as e:
    print(f"WARNING: Failed to import trading modules: {e}")
    print(f"Current directory: {Path(__file__).parent}")
    print(f"Looking for: paper_trading_coordinator.py")
    PaperTradingCoordinator = None
    MarketCalendar = None
    Exchange = None
    MarketStatus = None"""
    
    content = content.replace(old_import, new_import)
    
    # Fix 3: Add UTF-8 encoding support for logging
    old_logging = """# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/"""
    
    new_logging = """# Configure logging with UTF-8 encoding for Windows
import io

# Create logs directory if it doesn't exist
Path('logs').mkdir(exist_ok=True)

# Configure logging with UTF-8 support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/"""
    
    content = content.replace(old_logging, new_logging)
    
    # Fix 4: Add encoding parameter to FileHandler
    content = re.sub(
        r"logging\.FileHandler\('logs/(\w+_pipeline\.log)'\)",
        r"logging.FileHandler('logs/\1', encoding='utf-8')",
        content
    )
    
    # Fix 5: Add console UTF-8 support
    old_stream = """        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)"""
    
    new_stream = """        logging.StreamHandler(sys.stdout)  # Explicitly use stdout
    ]
)
logger = logging.getLogger(__name__)

# Set console encoding to UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass  # If reconfigure fails, fall back to default"""
    
    content = content.replace(old_stream, new_stream)
    
    # Fix 6: Replace emoji characters with ASCII
    emoji_replacements = {
        '[X]': '[ERROR]',
        '[OK]': '[OK]',
        '[!]': '[WARNING]',
        '[#]': '[INFO]',
        '[*]': '[TARGET]',
        '💰': '[MONEY]',
        '[UP]': '[UP]',
        '[DN]': '[DOWN]',
        '🔍': '[SCAN]',
        '⏰': '[TIME]',
        '[GLOBE]': '[GLOBAL]',
    }
    
    for emoji, replacement in emoji_replacements.items():
        content = content.replace(emoji, replacement)
    
    # Write back if changed
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [OK] Fixed successfully")
        return True
    else:
        print(f"  - No changes needed")
        return False

def main():
    """Fix all pipeline files"""
    print("=" * 70)
    print("PIPELINE IMPORT AND ENCODING FIX")
    print("=" * 70)
    
    pipeline_files = [
        'run_au_pipeline.py',
        'run_us_pipeline.py',
        'run_uk_pipeline.py',
        'run_au_pipeline_v1.3.13.py',
        'run_us_pipeline_v1.3.13.py',
        'run_uk_pipeline_v1.3.13.py',
    ]
    
    fixed = 0
    for filepath in pipeline_files:
        path = Path(filepath)
        if path.exists():
            if fix_pipeline_file(path):
                fixed += 1
        else:
            print(f"\nSkipping: {filepath} (not found)")
    
    print("\n" + "=" * 70)
    print(f"COMPLETE: Fixed {fixed} pipeline files")
    print("=" * 70)
    print("\nChanges made:")
    print("  1. Import path: parent.parent -> parent")
    print("  2. Better import error messages")
    print("  3. UTF-8 encoding for log files")
    print("  4. UTF-8 console output (Windows)")
    print("  5. Emoji characters -> ASCII equivalents")
    print("\nYou can now run the pipelines without import or encoding errors!")

if __name__ == "__main__":
    main()

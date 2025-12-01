"""
Debug Pipeline Import Issues
=============================

This script will show exactly where the TelegramNotifier import is failing.
"""

import sys
import traceback
from pathlib import Path

print("\n" + "="*80)
print("PIPELINE IMPORT DEBUG")
print("="*80)

print(f"\nCurrent directory: {Path.cwd()}")

# Step 1: Test the import directly
print("\n[STEP 1] Testing direct import...")
try:
    from models.notifications.telegram_notifier import TelegramNotifier
    print(f"✓ Direct import SUCCESS: {TelegramNotifier}")
except Exception as e:
    print(f"✗ Direct import FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 2: Test the way pipeline imports it
print("\n[STEP 2] Testing pipeline-style import (relative)...")
try:
    # This simulates what the pipeline does
    import models.screening.overnight_pipeline as pipeline_module
    print(f"✓ Pipeline module imported")
    
    # Check if TelegramNotifier is available in the module
    if hasattr(pipeline_module, 'TelegramNotifier'):
        print(f"✓ TelegramNotifier found in pipeline module: {pipeline_module.TelegramNotifier}")
    else:
        print("⚠️  TelegramNotifier not found as module attribute")
        print("   This might be OK if it's imported locally")
    
except Exception as e:
    print(f"✗ Pipeline import FAILED: {e}")
    traceback.print_exc()
    print("\nThis is the actual error!")
    sys.exit(1)

# Step 3: Try to create pipeline instance
print("\n[STEP 3] Testing pipeline instantiation...")
try:
    from models.screening.overnight_pipeline import OvernightPipeline
    print("✓ OvernightPipeline class imported")
    
    # Try to create instance
    pipeline = OvernightPipeline()
    print("✓ OvernightPipeline instance created!")
    print(f"   telegram attribute: {pipeline.telegram}")
    
except NameError as e:
    print(f"✗ NameError during pipeline creation: {e}")
    print("\nThis is the error you're seeing!")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"✗ Pipeline creation failed: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

# Success
print("\n" + "="*80)
print("ALL TESTS PASSED!")
print("="*80)
print("\n✓ TelegramNotifier imports correctly")
print("✓ Pipeline module loads correctly")
print("✓ Pipeline can be instantiated")
print("\nIf pipeline.bat still fails, the issue is with how/where it's being run.")
print("\n" + "="*80)

input("\nPress Enter to exit...")

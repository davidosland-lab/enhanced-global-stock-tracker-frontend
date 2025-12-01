================================================================================
KERAS 3 MODEL SAVING FIX - COMPLETE PATCH
================================================================================

QUICK START:
-----------
1. Extract this ZIP to: C:\Users\david\AATelS
2. Run: install_keras_fix.bat
3. Test: python finbert_v4.4.4\models\train_lstm.py --symbol BHP.AX --epochs 5
4. Done!


PROBLEM DESCRIPTION:
-------------------
Your system has TensorFlow 2.20.0 with Keras 3.11.3 installed.

Keras 3.x introduced a BREAKING CHANGE:
- Default save format changed from .h5 to .keras
- Saving to .h5 requires explicit: save_format='h5'
- Without this, model.save() SILENTLY FAILS

SYMPTOMS:
- Pipeline trains models successfully
- Only JSON metadata files created (lstm_A2M.AX_metadata.json)
- NO actual .h5 model files saved (A2M.AX_lstm_model.h5 missing)
- Pipeline retrains all 139 models every run (~2 hours wasted)
- No efficiency gains from cached models

ROOT CAUSE:
- File: finbert_v4.4.4/models/lstm_predictor.py
- Line 510: self.model.save(self.model_path)
- Missing: save_format='h5' parameter required by Keras 3


THE FIX:
-------
This patch adds save_format='h5' parameter to the model.save() call:

OLD CODE (Line 510):
    self.model.save(self.model_path)

NEW CODE:
    try:
        self.model.save(self.model_path, save_format='h5')
        logger.info(f"Model saved to {self.model_path} (Keras 3 format)")
    except Exception as keras_error:
        # Fallback for Keras 2.x
        self.model.save(self.model_path)
        logger.info(f"Model saved to {self.model_path} (legacy format)")


PACKAGE CONTENTS:
----------------
1. install_keras_fix.bat    - Automatic installer (RECOMMENDED)
2. apply_keras_fix.py       - Python script to apply fix
3. verify_keras_fix.py      - Verification script
4. test_single_model.bat    - Test script for single model
5. README.txt               - This file
6. TECHNICAL_DETAILS.txt    - Detailed technical information


INSTALLATION OPTIONS:
====================

OPTION 1: AUTOMATIC (Recommended)
---------------------------------
1. Extract ZIP to: C:\Users\david\AATelS
2. Double-click: install_keras_fix.bat
3. Follow on-screen prompts

The script will:
- Check your Python/TensorFlow/Keras versions
- Create automatic backup of original file
- Apply the fix
- Verify fix was applied correctly
- Run test to ensure model saving works

Expected output:
    [OK] Backup created
    [OK] Fix applied
    [OK] Verification passed
    [OK] Model saved successfully

Time required: 1-2 minutes


OPTION 2: MANUAL
---------------
1. Open: C:\Users\david\AATelS\finbert_v4.4.4\models\lstm_predictor.py
2. Find line ~510 in save_model() function:
   
   self.model.save(self.model_path)

3. Replace with:
   
   try:
       self.model.save(self.model_path, save_format='h5')
       logger.info(f"Model saved to {self.model_path} (Keras 3 format)")
   except Exception as keras_error:
       logger.warning(f"Keras 3 save failed: {keras_error}")
       self.model.save(self.model_path)
       logger.info(f"Model saved to {self.model_path} (legacy format)")

4. Save file
5. Run: verify_keras_fix.py

Time required: 2-3 minutes


VERIFICATION:
============

After installation, verify the fix:

1. Run verification script:
   python verify_keras_fix.py

2. Expected output:
   ✓ TensorFlow and Keras available
   ✓ Fix is applied! save_format='h5' found in code
   ✓ Model saved successfully with save_format='h5'
   ✓ Model file created
   ✓ Model loaded successfully

3. If all tests pass, the fix is working!


TESTING:
=======

Test with a single model (5 minutes):
   test_single_model.bat

OR manually:
   python finbert_v4.4.4\models\train_lstm.py --symbol BHP.AX --epochs 5

Expected results:
   ✓ Training completes successfully
   ✓ File created: models\BHP.AX_lstm_model.h5 (~500KB)
   ✓ File created: models\lstm_BHP.AX_metadata.json (~1KB)
   ✓ Log shows: "Model saved to models/lstm_model.h5 (Keras 3 format)"

Check file was created:
   dir models\BHP.AX_lstm_model.h5

File size should be ~500KB (not 0 bytes!)


FULL PIPELINE:
=============

Once verified, run the full pipeline:
   RUN_PIPELINE_TEST.bat

With the fix applied:
   ✓ Models train once and SAVE successfully
   ✓ 139 .h5 model files created (one per stock)
   ✓ Next run LOADS existing models (fast!)
   ✓ Only retrains if model >7 days old
   ✓ Pipeline runtime: 30-45 minutes (vs 2+ hours before)


EXPECTED RESULTS:
================

After running full pipeline, you should see:

C:\Users\david\AATelS\models\screening\models\
    A2M.AX_lstm_model.h5           (~500KB each)
    BHP.AX_lstm_model.h5
    CBA.AX_lstm_model.h5
    CSL.AX_lstm_model.h5
    ... (139 total .h5 files)
    
    lstm_A2M.AX_metadata.json      (~1-2KB each)
    lstm_BHP.AX_metadata.json
    lstm_CBA.AX_metadata.json
    ... (139 total .json files)

Total: 278 files (139 models + 139 metadata)


TROUBLESHOOTING:
===============

Issue: "ERROR: Cannot find finbert_v4.4.4\models\lstm_predictor.py"
Solution: Ensure you extracted ZIP to C:\Users\david\AATelS

Issue: "ERROR: Python not found"
Solution: Install Python or add to PATH

Issue: "ERROR: TensorFlow or Keras not installed"
Solution: Run: pip install tensorflow keras

Issue: "Verification failed"
Solution: Check output, may need manual fix (see OPTION 2)

Issue: Models still not saving after fix
Solution: 
   1. Run verify_keras_fix.py and check output
   2. Check logs: models\screening\logs\lstm_training.log
   3. Verify file permissions on models directory
   4. Try test_single_model.bat


BACKUP & ROLLBACK:
=================

The installer automatically creates a backup:
   finbert_v4.4.4\models\lstm_predictor.py.backup_YYYYMMDD_HHMMSS

To rollback (if needed):
   copy finbert_v4.4.4\models\lstm_predictor.py.backup_* finbert_v4.4.4\models\lstm_predictor.py


TECHNICAL SUPPORT:
=================

For detailed technical information, see: TECHNICAL_DETAILS.txt

Related documentation:
- Keras 3 Migration Guide: https://keras.io/guides/migrating_to_keras_3/
- TensorFlow Saving: https://www.tensorflow.org/guide/keras/save_and_serialize

Repository: github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
Branch: finbert-v4.0-development


SUMMARY:
=======

BEFORE FIX:
   ✗ Models train but don't save
   ✗ Only JSON metadata created
   ✗ Pipeline retrains 139 models every run
   ✗ Runtime: 2+ hours every time
   ✗ No efficiency gains

AFTER FIX:
   ✓ Models train AND save as .h5 files
   ✓ Both .h5 and .json files created
   ✓ Pipeline loads existing models
   ✓ Only retrains if needed (>7 days old)
   ✓ Runtime: 30-45 minutes
   ✓ Full efficiency gains realized


QUICK REFERENCE:
===============

Install:     install_keras_fix.bat
Verify:      python verify_keras_fix.py
Test:        test_single_model.bat
Full Run:    RUN_PIPELINE_TEST.bat
Check Models: dir /b models\screening\models\*.h5


================================================================================
Version: 1.0
Date: 2025-12-01
Applies To: TensorFlow 2.16+ with Keras 3.x
================================================================================

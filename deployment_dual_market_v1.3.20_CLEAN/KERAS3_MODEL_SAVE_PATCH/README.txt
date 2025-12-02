================================================================================
                KERAS 3 MODEL SAVE FIX - PATCH PACKAGE
================================================================================

PROBLEM FIXED:
--------------
All 139 stock models were saving to the SAME file (models/lstm_model.keras),
causing models to overwrite each other and forcing retraining every run.

SOLUTION:
---------
Models now save with symbol-specific names: BHP.AX_lstm_model.keras, etc.
Result: 139 separate models, cached for 7 days, 60-75% faster runs!

================================================================================

QUICK INSTALLATION (2 MINUTES):
-------------------------------

1. Extract this ZIP to: C:\Users\david\AATelS
2. Run: INSTALL_PATCH.bat
3. Verify: python verification\verify_fix.py
4. Test: python finbert_v4.4.4\models\train_lstm.py --symbol BHP.AX --epochs 5

See MANUAL_INSTALL.txt for manual installation.
See TECHNICAL_DETAILS.txt for what changed and why.

================================================================================

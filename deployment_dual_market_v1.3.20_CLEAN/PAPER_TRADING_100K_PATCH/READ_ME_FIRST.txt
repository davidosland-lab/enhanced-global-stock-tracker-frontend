=====================================================================
PAPER TRADING $100K PATCH - READ THIS FIRST!
=====================================================================

QUICK START (5 MINUTES)
=====================================================================

1. Extract this ZIP to: C:\Users\david\AATelS\

   Result:
   C:\Users\david\AATelS\
   ├── finbert_v4.4.4\              (your existing installation)
   └── PAPER_TRADING_100K_PATCH\    (NEW from this ZIP)

2. Open Command Prompt

3. Run these commands EXACTLY:

   cd C:\Users\david\AATelS
   PAPER_TRADING_100K_PATCH\INSTALL_SIMPLE.bat

4. Follow the on-screen instructions

=====================================================================
WHICH INSTALLER TO USE?
=====================================================================

This patch includes THREE installers:

1. INSTALL_SIMPLE.bat       ← START HERE! (RECOMMENDED)
   - Simple, clear output
   - Always stays open
   - Easy to see what happened
   - Best for first-time users

2. INSTALL_PATCH_V2.bat
   - More detailed verification
   - Good for advanced users
   - Shows [OK] for each step

3. INSTALL_PATCH.bat
   - Original version
   - Very strict verification
   - May fail on app_finbert_v4_dev.py

RECOMMENDATION: Use INSTALL_SIMPLE.bat unless you have a reason not to.

=====================================================================
COMMON MISTAKES TO AVOID
=====================================================================

❌ MISTAKE #1: Running from wrong directory

WRONG:
  cd C:\Users\david\AATelS\PAPER_TRADING_100K_PATCH
  INSTALL_SIMPLE.bat

CORRECT:
  cd C:\Users\david\AATelS
  PAPER_TRADING_100K_PATCH\INSTALL_SIMPLE.bat

❌ MISTAKE #2: Not extracting the ZIP first

You must extract the ZIP to C:\Users\david\AATelS\ before running.
Don't run the installer from inside WinRAR or 7-Zip!

❌ MISTAKE #3: Window closes too fast

If the window closes immediately:
- You're probably in the wrong directory
- Open a NEW Command Prompt
- Type: cd C:\Users\david\AATelS
- Type: dir (you should see both finbert_v4.4.4 and PAPER_TRADING_100K_PATCH)
- Then run: PAPER_TRADING_100K_PATCH\INSTALL_SIMPLE.bat

=====================================================================
COMPLETE INSTALLATION STEPS
=====================================================================

Step 1: Extract ZIP
   - Right-click PAPER_TRADING_100K_PATCH.zip
   - Select "Extract All..."
   - Choose: C:\Users\david\AATelS
   - Click "Extract"

Step 2: Open Command Prompt
   - Press Windows Key + R
   - Type: cmd
   - Press Enter

Step 3: Navigate to correct directory
   cd C:\Users\david\AATelS

Step 4: Verify you're in the right place
   dir
   
   You should see:
   - finbert_v4.4.4 (folder)
   - PAPER_TRADING_100K_PATCH (folder)

Step 5: Run the installer
   PAPER_TRADING_100K_PATCH\INSTALL_SIMPLE.bat

Step 6: Wait for "INSTALLATION COMPLETE!" message

Step 7: Reset your account
   cd finbert_v4.4.4
   python -c "from models.trading.paper_trading_engine import PaperTradingEngine; PaperTradingEngine().reset_account(100000); print('Reset to $100,000')"

Step 8: Verify the new balance
   python -c "from models.trading.paper_trading_engine import PaperTradingEngine; account = PaperTradingEngine().get_account_summary()['account']; print(f'Cash: ${account[\"cash_balance\"]:,.2f}')"

   Expected output: Cash: $100,000.00

Step 9: Test in Web UI (optional)
   python app_finbert_v4_dev.py
   Open: http://localhost:5000
   Check: Paper Trading tab should show $100,000.00

=====================================================================
IF THE INSTALLER CLOSES IMMEDIATELY
=====================================================================

The installer is closing because it can't find the required files.

This means either:
1. You're in the wrong directory, OR
2. You didn't extract the ZIP, OR
3. You extracted to the wrong location

FIX:
1. Open Command Prompt
2. Type: cd C:\Users\david\AATelS
3. Type: dir
4. Verify you see: finbert_v4.4.4 AND PAPER_TRADING_100K_PATCH
5. If you DON'T see both folders:
   - Find where you extracted the ZIP
   - Move PAPER_TRADING_100K_PATCH folder to C:\Users\david\AATelS\
6. Run: PAPER_TRADING_100K_PATCH\INSTALL_SIMPLE.bat

=====================================================================
MANUAL INSTALLATION (IF INSTALLER FAILS)
=====================================================================

If all installers fail, you can copy files manually:

1. Create backup
   mkdir C:\Users\david\AATelS\finbert_v4.4.4\BACKUP_MANUAL
   copy C:\Users\david\AATelS\finbert_v4.4.4\models\trading\*.py C:\Users\david\AATelS\finbert_v4.4.4\BACKUP_MANUAL\
   copy C:\Users\david\AATelS\finbert_v4.4.4\app_finbert_v4_dev.py C:\Users\david\AATelS\finbert_v4.4.4\BACKUP_MANUAL\
   copy C:\Users\david\AATelS\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html C:\Users\david\AATelS\finbert_v4.4.4\BACKUP_MANUAL\

2. Copy updated files (from PAPER_TRADING_100K_PATCH to finbert_v4.4.4)
   cd C:\Users\david\AATelS
   
   copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py finbert_v4.4.4\models\trading\
   
   copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\paper_trading_engine.py finbert_v4.4.4\models\trading\
   
   copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\portfolio_manager.py finbert_v4.4.4\models\trading\
   
   copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\app_finbert_v4_dev.py finbert_v4.4.4\
   
   copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html finbert_v4.4.4\templates\

3. Clear cache
   cd finbert_v4.4.4
   for /d /r models\trading %d in (__pycache__) do @if exist "%d" rd /s /q "%d"

4. Reset account
   python -c "from models.trading.paper_trading_engine import PaperTradingEngine; PaperTradingEngine().reset_account(100000); print('Done')"

5. Verify
   python -c "from models.trading.paper_trading_engine import PaperTradingEngine; account = PaperTradingEngine().get_account_summary()['account']; print(f'Cash: ${account[\"cash_balance\"]:,.2f}')"

=====================================================================
WHAT THIS PATCH DOES
=====================================================================

Changes paper trading account limit:
  FROM: $10,000
  TO:   $100,000

Files updated (5 total):
  1. models/trading/trade_database.py       (11 changes)
  2. models/trading/paper_trading_engine.py (1 change)
  3. models/trading/portfolio_manager.py    (1 change)
  4. app_finbert_v4_dev.py                  (6 changes)
  5. templates/finbert_v4_enhanced_ui.html  (3 changes)

Total: 22 changes across 5 files (10000 → 100000)

=====================================================================
ROLLBACK (IF YOU WANT TO REVERT)
=====================================================================

Your original files are backed up automatically.

Find your backup folder:
  dir C:\Users\david\AATelS\finbert_v4.4.4\BACKUP_*

Restore from backup:
  cd C:\Users\david\AATelS\finbert_v4.4.4
  copy BACKUP_SIMPLE_YYYYMMDD_HHMMSS\models\trading\*.py models\trading\
  copy BACKUP_SIMPLE_YYYYMMDD_HHMMSS\app_finbert_v4_dev.py .
  copy BACKUP_SIMPLE_YYYYMMDD_HHMMSS\templates\*.html templates\

Then reset to $10,000:
  python -c "from models.trading.paper_trading_engine import PaperTradingEngine; PaperTradingEngine().reset_account(10000); print('Reset to $10,000')"

=====================================================================
VERIFICATION
=====================================================================

After installation, verify the patch worked:

1. Check balance
   cd C:\Users\david\AATelS\finbert_v4.4.4
   python -c "from models.trading.paper_trading_engine import PaperTradingEngine; account = PaperTradingEngine().get_account_summary()['account']; print(f'Cash: ${account[\"cash_balance\"]:,.2f}')"
   
   Expected: Cash: $100,000.00

2. Check files contain 100000
   findstr /C:"100000" models\trading\trade_database.py
   findstr /C:"100000" models\trading\paper_trading_engine.py
   findstr /C:"$100,000" templates\finbert_v4_enhanced_ui.html
   
   Each should return matching lines

3. Web UI check
   python app_finbert_v4_dev.py
   Open: http://localhost:5000
   Paper Trading tab should show: $100,000.00

=====================================================================
HELP & TROUBLESHOOTING
=====================================================================

For more detailed help, see:
- TROUBLESHOOTING.txt (comprehensive guide)
- CHANGES.txt (what changed)
- ROLLBACK.txt (how to revert)

=====================================================================

QUICK SUMMARY:
1. Extract ZIP to C:\Users\david\AATelS\
2. cd C:\Users\david\AATelS
3. PAPER_TRADING_100K_PATCH\INSTALL_SIMPLE.bat
4. cd finbert_v4.4.4
5. python -c "from models.trading.paper_trading_engine import PaperTradingEngine; PaperTradingEngine().reset_account(100000); print('Done')"
6. python -c "from models.trading.paper_trading_engine import PaperTradingEngine; account = PaperTradingEngine().get_account_summary()['account']; print(f'Cash: ${account[\"cash_balance\"]:,.2f}')"

Expected: Cash: $100,000.00

DONE! 🎉

=====================================================================

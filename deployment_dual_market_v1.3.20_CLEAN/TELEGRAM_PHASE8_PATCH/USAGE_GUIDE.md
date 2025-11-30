# Telegram Phase 8 Integration - Usage Guide

## 📖 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation Methods](#installation-methods)
4. [Testing](#testing)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## Overview

This patch fixes the missing Phase 8 (Telegram Notifications) in your overnight pipelines. After applying this patch, you will receive Telegram messages with pipeline summaries and report files after each overnight run.

### What Was Wrong

Your pipeline log showed:
```
PHASE 7: EMAIL NOTIFICATIONS
Email notification failed: 'bool' object is not callable

PIPELINE EXECUTION SUMMARY
Status: SUCCESS
```

The pipeline stopped at Phase 7 and **never executed Phase 8** because the code was missing.

### What This Fixes

After patching:
```
PHASE 7: EMAIL NOTIFICATIONS
[email processing]

PHASE 8: TELEGRAM NOTIFICATIONS
Sending Telegram morning report notification...
✓ Telegram report sent: 2025-11-30_market_report.html
✓ CSV file sent: 2025-11-30_screening_results.csv

PIPELINE EXECUTION SUMMARY
Status: SUCCESS
```

---

## Prerequisites

### Required

✅ **Telegram Credentials Configured**
   - You've already set up Telegram (completed earlier)
   - `config/intraday_rescan_config.json` has bot_token and chat_id
   - The TelegramNotifier class works correctly

✅ **Python Environment**
   - Python 3.7+ installed
   - All pipeline dependencies installed

✅ **Git Repository**
   - Your project is in a git repository (for backup purposes)

### What You DON'T Need

❌ New Telegram credentials (you already have them)  
❌ Additional Python packages  
❌ Code modifications (the patcher does everything)  
❌ Configuration changes (your config is correct)

---

## Installation Methods

### Method 1: Automatic Installation (Recommended)

**Step 1:** Extract the patch ZIP

```cmd
# Extract TELEGRAM_PHASE8_PATCH.zip to your project root
# You should have: C:\Users\david\AATelS\TELEGRAM_PHASE8_PATCH\
```

**Step 2:** Run the installer

```cmd
cd C:\Users\david\AATelS\TELEGRAM_PHASE8_PATCH
runpatch.bat
```

**Step 3:** Follow the prompts

The installer will:
1. Check environment
2. Create backups
3. Check for existing Phase 8
4. Apply patches
5. Verify installation

**Step 4:** Review the results

Look for:
```
INSTALLATION COMPLETE!

Phase 8 (Telegram Notifications) has been successfully added!
```

### Method 2: Python-Only Installation

If you prefer to run Python directly:

```cmd
cd C:\Users\david\AATelS
python TELEGRAM_PHASE8_PATCH\apply_patch.py
```

This skips the batch file checks but still applies the patch.

### Method 3: Manual Installation

If automatic patching fails, see **Manual Installation** section below.

---

## Testing

### Quick Test (5 stocks, ~5 minutes)

**Australian Pipeline:**
```cmd
cd C:\Users\david\AATelS
python models\screening\overnight_pipeline.py --stocks-per-sector 5
```

**US Pipeline:**
```cmd
cd C:\Users\david\AATelS
python models\screening\us_overnight_pipeline.py --stocks-per-sector 5
```

### What to Look For

**In the console/log:**
```
================================================================================
PHASE 8: TELEGRAM NOTIFICATIONS
================================================================================
Sending Telegram morning report notification...
✓ Telegram report sent: 2025-11-30_market_report.html
✓ CSV file sent: 2025-11-30_screening_results.csv
```

**In Telegram:**
- Message from your bot
- Pipeline summary
- HTML report attachment
- CSV file attachment

### Full Pipeline Test

Once quick test works, run full pipeline:

```cmd
# Australian (default: 30 stocks per sector)
python models\screening\overnight_pipeline.py

# US (default: 30 stocks per sector)
python models\screening\us_overnight_pipeline.py
```

---

## Verification

### Check 1: Code Verification

Verify Phase 8 code exists:

```cmd
cd C:\Users\david\AATelS
findstr /C:"PHASE 8: TELEGRAM NOTIFICATIONS" models\screening\overnight_pipeline.py
findstr /C:"PHASE 8: TELEGRAM NOTIFICATIONS" models\screening\us_overnight_pipeline.py
```

**Expected output:**
```
models\screening\overnight_pipeline.py:501:                logger.info("PHASE 8: TELEGRAM NOTIFICATIONS")
models\screening\us_overnight_pipeline.py:478:                logger.info("PHASE 8: TELEGRAM NOTIFICATIONS")
```

### Check 2: Function Verification

Verify the Telegram function exists:

```cmd
findstr /C:"_send_telegram_report_notification" models\screening\overnight_pipeline.py
```

**Expected:** Multiple lines showing the function definition and calls

### Check 3: Log Verification

After running a test, check the log:

```cmd
# Australian pipeline
type logs\overnight_pipeline.log | findstr "PHASE 8"

# US pipeline  
type logs\screening\us\us_overnight_pipeline.log | findstr "PHASE 8"
```

**Expected:**
```
PHASE 8: TELEGRAM NOTIFICATIONS
Sending Telegram morning report notification...
✓ Telegram report sent
✓ CSV file sent
```

### Check 4: Telegram Verification

Open Telegram and verify:
- ✅ Message received from your bot
- ✅ Summary shows correct stock count
- ✅ HTML report attached
- ✅ CSV file attached
- ✅ Timestamp is correct

---

## Troubleshooting

### Issue: Patch Installer Can't Find Files

**Error:**
```
ERROR: overnight_pipeline.py not found!
```

**Solutions:**

1. **Check your directory:**
   ```cmd
   cd C:\Users\david\AATelS
   dir models\screening\overnight_pipeline.py
   ```
   
   If file doesn't exist, you're in the wrong directory.

2. **Run from patch directory:**
   ```cmd
   cd C:\Users\david\AATelS\TELEGRAM_PHASE8_PATCH
   runpatch.bat
   ```

3. **Check extraction path:**
   Make sure you extracted the ZIP to the right place:
   ```
   C:\Users\david\AATelS\TELEGRAM_PHASE8_PATCH\
   ```

### Issue: "Phase 8 already exists"

**Message:**
```
Phase 8 already exists in overnight_pipeline.py
```

**Solution:** This is GOOD! The patch is already installed. No action needed.

### Issue: Patch Applied But No Telegram Message

**Symptoms:**
- Patch installed successfully
- Phase 8 appears in log
- But no Telegram message received

**Diagnosis:**

1. **Check the log for errors:**
   ```cmd
   type logs\overnight_pipeline.log | findstr "Telegram"
   ```

2. **Look for:**
   - "Telegram notifications disabled" → Config issue
   - "Telegram notification failed" → Check error message
   - "✗" symbols → Something went wrong

**Common causes:**

1. **Config not loaded:**
   - Verify `config/intraday_rescan_config.json` exists
   - Check `notifications.telegram` section
   - Run `python check_telegram_setup.py`

2. **Telegram credentials invalid:**
   - Test with `python test_morning_report_telegram.py`
   - Regenerate bot token from @BotFather if needed
   - Verify chat_id with @userinfobot

3. **self.telegram is None:**
   - Check startup logs for "✓ Telegram notifications enabled"
   - If you see "disabled", config wasn't loaded properly

### Issue: Backup Files Exist

**Warning:**
```
overnight_pipeline.py.backup already exists
```

**Solution:**

Delete or rename old backups:
```cmd
cd C:\Users\david\AATelS\models\screening
del overnight_pipeline.py.backup
del us_overnight_pipeline.py.backup
```

Then re-run the patcher.

### Issue: Manual Rollback Needed

If something went wrong and you need to restore:

```cmd
cd C:\Users\david\AATelS\models\screening

# Restore Australian pipeline
copy overnight_pipeline.py.backup overnight_pipeline.py /Y

# Restore US pipeline
copy us_overnight_pipeline.py.backup us_overnight_pipeline.py /Y
```

---

## Manual Installation

If automatic patching fails, you can manually add Phase 8:

### Step 1: Open the Pipeline File

Open `models/screening/overnight_pipeline.py` in your editor

### Step 2: Find Phase 7

Search for:
```python
logger.warning(f"Email notification failed: {str(e)}")
# Don't fail the pipeline if emails fail
```

### Step 3: Add Phase 8 Code

Right after the Phase 7 try/except block, add:

```python
            # Send Telegram notification
            try:
                logger.info("\n" + "="*80)
                logger.info("PHASE 8: TELEGRAM NOTIFICATIONS")
                logger.info("="*80)
                
                self._send_telegram_report_notification(
                    report_path=Path(report_path),
                    stocks_count=len(scanned_stocks),
                    top_opportunities=len([s for s in final_opportunities if s.get('signal_strength', 0) >= 70]),
                    execution_time=elapsed_time/60
                )
            except Exception as e:
                logger.warning(f"Telegram notification failed: {str(e)}")
                # Don't fail the pipeline if Telegram fails
```

### Step 4: Add the Telegram Function

Search for `def main():` and add this **BEFORE** it:

```python
    def _send_telegram_report_notification(self, report_path: Path, stocks_count: int, 
                                          top_opportunities: int, execution_time: float):
        """Send morning report notification via Telegram"""
        if self.telegram is None:
            logger.debug("Telegram notifications disabled, skipping")
            return
        
        try:
            # Prepare market summary
            market_summary = f"""🇦🇺 *ASX Market Morning Report*

📊 *Pipeline Summary:*
• Total Stocks Scanned: {stocks_count}
• High-Quality Opportunities (≥70%): {top_opportunities}
• Execution Time: {execution_time:.1f} minutes
• Report Generated: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}

📁 Report files generated:
• HTML Report (with charts)
• CSV Export (for Excel)
• Pipeline Results (JSON)

✅ *Pipeline Status: COMPLETE*"""
            
            # Get report directory and find all related files
            report_dir = report_path.parent
            timestamp = report_path.stem.split('_')[-1]
            
            # Find related files (HTML, CSV)
            html_files = list(report_dir.glob(f'*{timestamp}*.html'))
            csv_files = list(report_dir.glob(f'*{timestamp}*.csv'))
            
            # Send morning report with attachments
            logger.info("Sending Telegram morning report notification...")
            
            if html_files:
                self.telegram.send_morning_report(
                    report_files=[str(html_files[0])],
                    market_summary=market_summary
                )
                logger.info(f"✓ Telegram report sent: {html_files[0].name}")
            else:
                self.telegram.send_message(market_summary)
                logger.info("✓ Telegram summary sent (text-only)")
            
            if csv_files:
                try:
                    self.telegram.send_document(
                        document_path=str(csv_files[0]),
                        caption=f"📊 ASX Market Screening Results - {datetime.now(self.timezone).strftime('%Y-%m-%d')}"
                    )
                    logger.info(f"✓ CSV file sent: {csv_files[0].name}")
                except Exception as csv_error:
                    logger.warning(f"CSV file send failed: {csv_error}")
            
        except Exception as e:
            logger.error(f"✗ Telegram notification failed: {e}")
            logger.error(traceback.format_exc())
```

### Step 5: Save and Test

Save the file and run a test:
```cmd
python models\screening\overnight_pipeline.py --stocks-per-sector 5
```

### Step 6: Repeat for US Pipeline

Do the same for `us_overnight_pipeline.py`, but change:
- `🇦🇺 *ASX` → `🇺🇸 *US`
- `ASX Market` → `US Market`

---

## Success Checklist

After installation, verify:

- [ ] Patch installed without errors
- [ ] Backup files created
- [ ] Phase 8 code exists in overnight_pipeline.py
- [ ] Phase 8 code exists in us_overnight_pipeline.py
- [ ] _send_telegram_report_notification() function exists
- [ ] Quick test shows Phase 8 in log
- [ ] Telegram message received
- [ ] HTML report attached
- [ ] CSV file attached
- [ ] Pipeline completes successfully

---

## Next Steps

Once the patch is installed and working:

1. **Run full pipelines regularly:**
   ```cmd
   python models\screening\overnight_pipeline.py
   python models\screening\us_overnight_pipeline.py
   ```

2. **Check Telegram for reports each morning**

3. **Review the attached HTML reports for opportunities**

4. **Export CSV data to Excel for further analysis**

---

**Questions?** Check the main README.md or review your pipeline logs for detailed error messages.

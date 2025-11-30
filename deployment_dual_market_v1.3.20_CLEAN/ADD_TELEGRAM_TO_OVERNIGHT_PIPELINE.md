# Add Telegram Notifications (Phase 8) to overnight_pipeline.py

## Location
`C:\Users\david\AATelS\models\screening\overnight_pipeline.py`

## Instructions

### Step 1: Find the Email Notification Section

Search for this text in the file:
```python
logger.info("✓ Email notifications completed")
```

### Step 2: Add Phase 8 Code

**Right after** the email notification try/except block ends (after the `logger.warning` line for email failures), add this code:

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

### Step 3: Add the Telegram Function

At the end of the `OvernightPipeline` class (before the `main()` function), add this method:

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
            timestamp = report_path.stem.split('_')[-1]  # Extract timestamp from filename
            
            # Find related files (HTML, CSV)
            html_files = list(report_dir.glob(f'*{timestamp}*.html'))
            csv_files = list(report_dir.glob(f'*{timestamp}*.csv'))
            
            # Send morning report with attachments
            logger.info("Sending Telegram morning report notification...")
            
            if html_files:
                # Send HTML report
                self.telegram.send_morning_report(
                    report_files=[str(html_files[0])],
                    market_summary=market_summary
                )
                logger.info(f"✓ Telegram report sent: {html_files[0].name}")
            else:
                # Send text-only summary if no HTML
                self.telegram.send_message(market_summary)
                logger.info("✓ Telegram summary sent (text-only)")
            
            # Optionally send CSV as separate attachment
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

## Quick Copy-Paste Version

Or use this Python script to automatically patch the file:

Save this as `patch_overnight_telegram.py` in `C:\Users\david\AATelS\`:

```python
import re

# Read the file
with open('models/screening/overnight_pipeline.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if Phase 8 already exists
if 'PHASE 8: TELEGRAM NOTIFICATIONS' in content:
    print("✓ Phase 8 already exists in the file!")
    exit(0)

# Find the insertion point (after email notification error handling)
pattern = r"(except Exception as e:\s+logger\.warning\(f\"Email notification failed: \{str\(e\)\}\"\)\s+# Don't fail the pipeline if emails fail)"

phase8_code = r'''\1
            
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
                # Don't fail the pipeline if Telegram fails'''

# Apply the patch
new_content = re.sub(pattern, phase8_code, content)

if new_content == content:
    print("❌ Could not find insertion point. Manual edit required.")
    print("Search for: 'Email notification failed' and add Phase 8 code after it.")
    exit(1)

# Find where to add the _send_telegram_report_notification method
# Look for the last method before main() or at the end of the class
method_code = '''
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
            timestamp = report_path.stem.split('_')[-1]  # Extract timestamp from filename
            
            # Find related files (HTML, CSV)
            html_files = list(report_dir.glob(f'*{timestamp}*.html'))
            csv_files = list(report_dir.glob(f'*{timestamp}*.csv'))
            
            # Send morning report with attachments
            logger.info("Sending Telegram morning report notification...")
            
            if html_files:
                # Send HTML report
                self.telegram.send_morning_report(
                    report_files=[str(html_files[0])],
                    market_summary=market_summary
                )
                logger.info(f"✓ Telegram report sent: {html_files[0].name}")
            else:
                # Send text-only summary if no HTML
                self.telegram.send_message(market_summary)
                logger.info("✓ Telegram summary sent (text-only)")
            
            # Optionally send CSV as separate attachment
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

'''

# Find insertion point before main() function
if '\ndef main():' in new_content:
    new_content = new_content.replace('\ndef main():', method_code + '\ndef main():')
else:
    # Add at the end of file
    new_content += method_code

# Write the patched file
with open('models/screening/overnight_pipeline.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Successfully patched overnight_pipeline.py with Phase 8!")
print("   Next: Run the pipeline and check for 'PHASE 8: TELEGRAM NOTIFICATIONS' in the log")
```

Then run:
```bash
cd C:\Users\david\AATelS
python patch_overnight_telegram.py
```

## Verification

After patching, run:
```bash
python models/screening/overnight_pipeline.py --stocks-per-sector 5
```

You should see in the log:
```
================================================================================
PHASE 8: TELEGRAM NOTIFICATIONS
================================================================================
Sending Telegram morning report notification...
✓ Telegram report sent: 2025-11-30_market_report.html
✓ CSV file sent: 2025-11-30_screening_results.csv
```

And receive the Telegram message!

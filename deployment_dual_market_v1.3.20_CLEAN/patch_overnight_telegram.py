"""
Automatic Patcher: Add Telegram Phase 8 to overnight_pipeline.py

This script automatically adds Telegram notification support (Phase 8)
to your overnight_pipeline.py file.

Usage:
    cd C:\Users\david\AATelS
    python patch_overnight_telegram.py
"""

import re
import shutil
from pathlib import Path

def main():
    pipeline_file = Path('models/screening/overnight_pipeline.py')
    
    if not pipeline_file.exists():
        print(f"❌ Error: {pipeline_file} not found!")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Make sure you're in C:\\Users\\david\\AATelS")
        return False
    
    # Create backup
    backup_file = pipeline_file.with_suffix('.py.backup')
    shutil.copy2(pipeline_file, backup_file)
    print(f"✓ Backup created: {backup_file}")
    
    # Read the file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Phase 8 already exists
    if 'PHASE 8: TELEGRAM NOTIFICATIONS' in content:
        print("✓ Phase 8 already exists in the file!")
        return True
    
    print("Adding Phase 8 to the pipeline...")
    
    # Step 1: Add Phase 8 execution code after email notifications
    # Find the email notification error handling
    email_pattern = r'(logger\.warning\(f"Email notification failed: \{str\(e\)\}"\)\s+# Don\'t fail the pipeline if emails fail\s+)'
    
    phase8_call = r'''\1
            # Send Telegram notification
            try:
                logger.info("\\n" + "="*80)
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
            
'''
    
    new_content = re.sub(email_pattern, phase8_call, content, count=1)
    
    if new_content == content:
        print("❌ Could not find email notification section")
        print("   Manual edit required - see ADD_TELEGRAM_TO_OVERNIGHT_PIPELINE.md")
        return False
    
    print("✓ Added Phase 8 call")
    
    # Step 2: Add the _send_telegram_report_notification method
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
    
    # Find insertion point - before "def main():" or at end of class
    if '\ndef main():' in new_content:
        new_content = new_content.replace('\ndef main():', method_code + '\ndef main():')
        print("✓ Added _send_telegram_report_notification method")
    elif '\n\ndef main():' in new_content:
        new_content = new_content.replace('\n\ndef main():', method_code + '\n\ndef main():')
        print("✓ Added _send_telegram_report_notification method")
    else:
        print("❌ Could not find 'def main():' - adding at end")
        new_content += '\n' + method_code
    
    # Write the patched file
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\n" + "="*80)
    print("✅ SUCCESS! overnight_pipeline.py has been patched with Phase 8")
    print("="*80)
    print("\nNext steps:")
    print("1. Test with: python models/screening/overnight_pipeline.py --stocks-per-sector 5")
    print("2. Look for 'PHASE 8: TELEGRAM NOTIFICATIONS' in the log")
    print("3. Check your Telegram for the morning report!")
    print(f"\nBackup saved as: {backup_file}")
    
    return True

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

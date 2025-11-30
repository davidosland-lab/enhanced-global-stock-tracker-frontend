"""
Telegram Phase 8 Integration Patcher
Automatically adds Phase 8 (Telegram Notifications) to overnight pipelines
"""

import re
import shutil
from pathlib import Path
from typing import Tuple

# ANSI color codes for Windows (basic)
GREEN = ''
RED = ''
YELLOW = ''
RESET = ''

def patch_pipeline(pipeline_file: Path, market: str) -> Tuple[bool, str]:
    """
    Patch a pipeline file to add Phase 8 Telegram notifications
    
    Args:
        pipeline_file: Path to the pipeline file
        market: Market name (ASX or US) for the notification message
        
    Returns:
        Tuple of (success, message)
    """
    if not pipeline_file.exists():
        return False, f"{pipeline_file} not found"
    
    # Read the file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Phase 8 already exists
    if 'PHASE 8: TELEGRAM NOTIFICATIONS' in content:
        return True, f"Phase 8 already exists in {pipeline_file.name}"
    
    print(f"\n  Patching {pipeline_file.name}...")
    
    # Step 1: Add Phase 8 execution code after email notifications
    # Look for the email notification error handling
    email_pattern = r'(logger\.warning\(f"Email notification failed: \{str\(e\)\}"\)\s*\n\s*# Don\'t fail the pipeline if emails fail\s*\n)'
    
    # Market-specific emoji
    market_emoji = "🇦🇺 *ASX" if market == "ASX" else "🇺🇸 *US"
    
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
        return False, f"Could not find email notification section in {pipeline_file.name}"
    
    print(f"    ✓ Added Phase 8 execution code")
    
    # Step 2: Add the _send_telegram_report_notification method
    method_code = f'''
    def _send_telegram_report_notification(self, report_path: Path, stocks_count: int, 
                                          top_opportunities: int, execution_time: float):
        """Send morning report notification via Telegram"""
        if self.telegram is None:
            logger.debug("Telegram notifications disabled, skipping")
            return
        
        try:
            # Prepare market summary
            market_summary = f"""{market_emoji} Market Morning Report*

📊 *Pipeline Summary:*
• Total Stocks Scanned: {{stocks_count}}
• High-Quality Opportunities (≥70%): {{top_opportunities}}
• Execution Time: {{execution_time:.1f}} minutes
• Report Generated: {{datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}}

📁 Report files generated:
• HTML Report (with charts)
• CSV Export (for Excel)
• Pipeline Results (JSON)

✅ *Pipeline Status: COMPLETE*"""
            
            # Get report directory and find all related files
            report_dir = report_path.parent
            timestamp = report_path.stem.split('_')[-1]  # Extract timestamp from filename
            
            # Find related files (HTML, CSV)
            html_files = list(report_dir.glob(f'*{{timestamp}}*.html'))
            csv_files = list(report_dir.glob(f'*{{timestamp}}*.csv'))
            
            # Send morning report with attachments
            logger.info("Sending Telegram morning report notification...")
            
            if html_files:
                # Send HTML report
                self.telegram.send_morning_report(
                    report_files=[str(html_files[0])],
                    market_summary=market_summary
                )
                logger.info(f"✓ Telegram report sent: {{html_files[0].name}}")
            else:
                # Send text-only summary if no HTML
                self.telegram.send_message(market_summary)
                logger.info("✓ Telegram summary sent (text-only)")
            
            # Optionally send CSV as separate attachment
            if csv_files:
                try:
                    self.telegram.send_document(
                        document_path=str(csv_files[0]),
                        caption=f"📊 {market} Market Screening Results - {{datetime.now(self.timezone).strftime('%Y-%m-%d')}}"
                    )
                    logger.info(f"✓ CSV file sent: {{csv_files[0].name}}")
                except Exception as csv_error:
                    logger.warning(f"CSV file send failed: {{csv_error}}")
            
        except Exception as e:
            logger.error(f"✗ Telegram notification failed: {{e}}")
            logger.error(traceback.format_exc())

'''
    
    # Find insertion point - before "def main():" or at end of class
    if '\ndef main():' in new_content:
        new_content = new_content.replace('\ndef main():', method_code + '\ndef main():')
        print(f"    ✓ Added _send_telegram_report_notification() method")
    elif '\n\ndef main():' in new_content:
        new_content = new_content.replace('\n\ndef main():', method_code + '\n\ndef main():')
        print(f"    ✓ Added _send_telegram_report_notification() method")
    else:
        # Try to find class end
        class_pattern = r'(\n\n# ={70,}\n# MAIN ENTRY POINT)'
        if re.search(class_pattern, new_content):
            new_content = re.sub(class_pattern, method_code + r'\1', new_content)
            print(f"    ✓ Added _send_telegram_report_notification() method")
        else:
            return False, f"Could not find insertion point for method in {pipeline_file.name}"
    
    # Write the patched file
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, f"Successfully patched {pipeline_file.name}"

def main():
    """Main patcher execution"""
    print("\n" + "="*80)
    print("TELEGRAM PHASE 8 INTEGRATION PATCHER")
    print("="*80)
    
    # Define pipeline files
    pipelines = [
        (Path('models/screening/overnight_pipeline.py'), 'ASX'),
        (Path('models/screening/us_overnight_pipeline.py'), 'US'),
    ]
    
    success_count = 0
    already_patched_count = 0
    failed_count = 0
    
    for pipeline_file, market in pipelines:
        if not pipeline_file.exists():
            print(f"\n  ⊘ {pipeline_file.name} not found - skipping")
            continue
        
        success, message = patch_pipeline(pipeline_file, market)
        
        if success:
            if "already exists" in message:
                print(f"  ✓ {message}")
                already_patched_count += 1
            else:
                print(f"  ✓ {message}")
                success_count += 1
        else:
            print(f"  ✗ {message}")
            failed_count += 1
    
    # Summary
    print("\n" + "="*80)
    print("PATCH SUMMARY")
    print("="*80)
    print(f"  Newly patched:     {success_count}")
    print(f"  Already patched:   {already_patched_count}")
    print(f"  Failed:            {failed_count}")
    print("="*80)
    
    if failed_count > 0:
        print("\n⚠ Some pipelines failed to patch!")
        print("  Please check the error messages above.")
        print("  Your backups are safe (.backup files)")
        return 1
    
    if success_count == 0 and already_patched_count > 0:
        print("\n✓ All pipelines already have Phase 8 installed!")
        return 0
    
    if success_count > 0:
        print("\n✓ Patch applied successfully!")
        print(f"  {success_count} pipeline(s) updated")
        return 0
    
    return 0

if __name__ == '__main__':
    import sys
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

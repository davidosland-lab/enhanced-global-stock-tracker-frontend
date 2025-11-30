"""
Pipeline Integration Script for Macro News Monitor
Automatically adds macro news integration code to your pipeline files
"""

import re
import shutil
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the file"""
    backup_path = str(file_path) + '.before_macro_integration'
    shutil.copy2(file_path, backup_path)
    print(f"  ✓ Backup created: {backup_path}")
    return backup_path

def integrate_us_pipeline():
    """Integrate macro news into US overnight pipeline"""
    pipeline_file = Path('models/screening/us_overnight_pipeline.py')
    
    if not pipeline_file.exists():
        print(f"\n⊘ {pipeline_file} not found - skipping")
        return False
    
    print(f"\n[Integrating US Pipeline]")
    
    # Read the file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already integrated
    if 'MacroNewsMonitor' in content:
        print("  ✓ Already integrated - skipping")
        return True
    
    # Backup
    backup_file(pipeline_file)
    
    # Step 1: Add import at top
    import_pattern = r'(from \.us_market_regime_engine import USMarketRegimeEngine)'
    import_code = r'''\1

# Macro news monitoring
try:
    from .macro_news_monitor import MacroNewsMonitor
except ImportError:
    MacroNewsMonitor = None'''
    
    if re.search(import_pattern, content):
        content = re.sub(import_pattern, import_code, content, count=1)
        print("  ✓ Added import statement")
    else:
        print("  ✗ Could not find import section")
        return False
    
    # Step 2: Add initialization in __init__
    init_pattern = r'(self\.regime_engine = USMarketRegimeEngine\(\)[\s\S]*?logger\.info\("✓ US Market Regime Engine initialized"\))'
    init_code = r'''\1
            
            # Optional: Macro News Monitor
            if MacroNewsMonitor is not None:
                self.macro_monitor = MacroNewsMonitor(market='US')
                logger.info("✓ Macro News Monitor enabled (Fed announcements)")
            else:
                self.macro_monitor = None
                logger.info("  Macro News Monitor disabled")'''
    
    if re.search(init_pattern, content):
        content = re.sub(init_pattern, init_code, content, count=1)
        print("  ✓ Added initialization code")
    else:
        print("  ✗ Could not find initialization section")
        return False
    
    # Step 3: Add macro news fetching in sentiment analysis
    sentiment_pattern = r'(sentiment = self\.market_monitor\.get_market_sentiment\(\)[\s\S]*?logger\.info\(f"  Recommendation: \{sentiment\[\'recommendation\'\]\[\'stance\'\]\}"\))'
    sentiment_code = r'''\1
            
            # Fetch macro news sentiment (Fed announcements, etc.)
            if self.macro_monitor is not None:
                try:
                    logger.info("")
                    macro_news = self.macro_monitor.get_macro_sentiment()
                    
                    # Add macro news to sentiment
                    sentiment['macro_news'] = macro_news
                    
                    # Adjust overall sentiment based on macro news
                    if macro_news['sentiment_score'] != 0:
                        # Macro news has 20% weight on overall sentiment
                        macro_adjustment = macro_news['sentiment_score'] * 10  # -10 to +10 scale
                        original_score = sentiment['overall']['score']
                        adjusted_score = original_score + macro_adjustment
                        adjusted_score = max(0, min(100, adjusted_score))  # Clamp to 0-100
                        
                        logger.info(f"  Macro News Impact: {macro_adjustment:+.1f} points")
                        logger.info(f"  Adjusted Sentiment: {original_score:.1f} → {adjusted_score:.1f}")
                        
                        sentiment['overall']['score'] = adjusted_score
                        sentiment['overall']['macro_adjusted'] = True
                    
                except Exception as e:
                    logger.warning(f"Macro news fetch failed: {e}")
                    sentiment['macro_news'] = None
            else:
                sentiment['macro_news'] = None'''
    
    if re.search(sentiment_pattern, content):
        content = re.sub(sentiment_pattern, sentiment_code, content, count=1)
        print("  ✓ Added sentiment adjustment code")
    else:
        print("  ✗ Could not find sentiment section")
        return False
    
    # Write the modified file
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✓ US pipeline integration complete!")
    return True

def integrate_asx_pipeline():
    """Integrate macro news into ASX overnight pipeline"""
    pipeline_file = Path('models/screening/overnight_pipeline.py')
    
    if not pipeline_file.exists():
        print(f"\n⊘ {pipeline_file} not found - skipping")
        return False
    
    print(f"\n[Integrating ASX Pipeline]")
    
    # Read the file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already integrated
    if 'MacroNewsMonitor' in content:
        print("  ✓ Already integrated - skipping")
        return True
    
    # Backup
    backup_file(pipeline_file)
    
    # Step 1: Add import
    import_pattern = r'(from \.event_risk_guard import EventRiskGuard)'
    import_code = r'''\1

# Macro news monitoring
try:
    from .macro_news_monitor import MacroNewsMonitor
except ImportError:
    MacroNewsMonitor = None'''
    
    if re.search(import_pattern, content):
        content = re.sub(import_pattern, import_code, content, count=1)
        print("  ✓ Added import statement")
    else:
        print("  ✗ Could not find import section")
        return False
    
    # Step 2: Add initialization
    init_pattern = r'(if EmailNotifier is not None:[\s\S]*?else:[\s\S]*?self\.notifier = None[\s\S]*?logger\.info\("  Email notifications disabled \(send_notification module not found\)"\))'
    init_code = r'''\1
            
            # Optional: Macro News Monitor
            if MacroNewsMonitor is not None:
                self.macro_monitor = MacroNewsMonitor(market='ASX')
                logger.info("✓ Macro News Monitor enabled (RBA/economic data)")
            else:
                self.macro_monitor = None
                logger.info("  Macro News Monitor disabled")'''
    
    if re.search(init_pattern, content):
        content = re.sub(init_pattern, init_code, content, count=1)
        print("  ✓ Added initialization code")
    else:
        print("  ✗ Could not find initialization section")
        return False
    
    # Step 3: Add macro news fetching
    sentiment_pattern = r'(logger\.info\(f"  Recommendation: \{sentiment\[\'recommendation\'\]\[\'stance\'\]\}"\))'
    sentiment_code = r'''\1
            
            # Fetch macro news sentiment (RBA announcements, etc.)
            if self.macro_monitor is not None:
                try:
                    logger.info("")
                    macro_news = self.macro_monitor.get_macro_sentiment()
                    
                    # Add macro news to sentiment
                    sentiment['macro_news'] = macro_news
                    
                    # Adjust overall sentiment based on macro news
                    if macro_news['sentiment_score'] != 0:
                        # Macro news has 20% weight on overall sentiment
                        macro_adjustment = macro_news['sentiment_score'] * 10  # -10 to +10 scale
                        original_score = sentiment['sentiment_score']
                        adjusted_score = original_score + macro_adjustment
                        adjusted_score = max(0, min(100, adjusted_score))  # Clamp to 0-100
                        
                        logger.info(f"  Macro News Impact: {macro_adjustment:+.1f} points")
                        logger.info(f"  Adjusted Sentiment: {original_score:.1f} → {adjusted_score:.1f}")
                        
                        sentiment['sentiment_score'] = adjusted_score
                        sentiment['macro_adjusted'] = True
                    
                except Exception as e:
                    logger.warning(f"Macro news fetch failed: {e}")
                    sentiment['macro_news'] = None
            else:
                sentiment['macro_news'] = None'''
    
    if re.search(sentiment_pattern, content):
        content = re.sub(sentiment_pattern, sentiment_code, content, count=1)
        print("  ✓ Added sentiment adjustment code")
    else:
        print("  ✗ Could not find sentiment section")
        return False
    
    # Write the modified file
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✓ ASX pipeline integration complete!")
    return True

def main():
    """Main integration process"""
    print("="*80)
    print("MACRO NEWS MONITOR - PIPELINE INTEGRATION")
    print("="*80)
    
    print("\nThis script will add macro news monitoring to your pipelines.")
    print("Backups will be created automatically.\n")
    
    input("Press Enter to continue...")
    
    # Integrate both pipelines
    us_success = integrate_us_pipeline()
    asx_success = integrate_asx_pipeline()
    
    # Summary
    print("\n" + "="*80)
    print("INTEGRATION SUMMARY")
    print("="*80)
    
    if us_success:
        print("✓ US Pipeline: INTEGRATED")
    else:
        print("✗ US Pipeline: FAILED or SKIPPED")
    
    if asx_success:
        print("✓ ASX Pipeline: INTEGRATED")
    else:
        print("✗ ASX Pipeline: FAILED or SKIPPED")
    
    if us_success or asx_success:
        print("\n✓ Integration complete!")
        print("\nNext steps:")
        print("  1. Test: python test_macro.py")
        print("  2. Run pipeline: python models\\screening\\us_overnight_pipeline.py --stocks-per-sector 5")
        print("  3. Look for 'MACRO NEWS ANALYSIS' in output")
        print("\nBackups saved with .before_macro_integration extension")
    else:
        print("\n✗ Integration failed!")
        print("  Check error messages above")
        print("  You may need to integrate manually")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nIntegration cancelled by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

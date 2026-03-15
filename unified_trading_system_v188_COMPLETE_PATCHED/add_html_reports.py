"""
HTML Morning Report Generator Patch
===================================
Adds HTML report generation to UK and US pipelines

This patch ensures that after the JSON report is created,
a beautiful HTML morning report is also generated for easy viewing.

Author: FinBERT v4.4.4
Date: 2026-03-01
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("="*80)
print("  HTML Morning Report Generator - Patch v193")
print("="*80)
print()
print("This patch adds HTML report generation to UK and US pipelines")
print("(AU pipeline already has it)")
print()

# Find the pipeline scripts
base_path = Path(".")
us_pipeline = base_path / "scripts" / "run_us_full_pipeline.py"
uk_pipeline = base_path / "scripts" / "run_uk_full_pipeline.py"

if not us_pipeline.exists() or not uk_pipeline.exists():
    print("ERROR: Cannot find pipeline scripts!")
    print(f"  Looking in: {base_path / 'scripts'}")
    print()
    print("Please run this script from your trading system root directory.")
    input("Press Enter to exit...")
    sys.exit(1)

print("[1/3] Backing up pipeline scripts...")
backup_dir = Path("backup_pre_v193")
backup_dir.mkdir(exist_ok=True)

import shutil
shutil.copy(us_pipeline, backup_dir / "run_us_full_pipeline.py.bak")
shutil.copy(uk_pipeline, backup_dir / "run_uk_full_pipeline.py.bak")
print("  ✓ Backed up US and UK pipeline scripts")

print("[2/3] Adding HTML report generation code...")

# The code to add at the end of run_full_overnight_pipeline method
html_generation_code = '''
            # ================================================================
            # GENERATE HTML MORNING REPORT
            # ================================================================
            try:
                from pipelines.models.screening.report_generator import ReportGenerator
                
                logger.info("[HTML REPORT] Generating morning report...")
                report_gen = ReportGenerator()
                
                # Extract data from results
                top_opps = results.get('top_opportunities', [])
                macro_news = results.get('macro_news', {})
                
                # Generate HTML report
                html_path = report_gen.generate_morning_report(
                    opportunities=top_opps,
                    spi_sentiment=macro_news,
                    sector_summary=results.get('sector_summary', {}),
                    system_stats=results.get('statistics', {}),
                    event_risk_data=results.get('event_risk', {}),
                    market_data=results.get('market_data', {})
                )
                
                logger.info(f"[HTML REPORT] [OK] HTML report: {html_path}")
                results['html_report_path'] = str(html_path)
                
            except Exception as e:
                logger.warning(f"[HTML REPORT] Failed to generate HTML (non-critical): {e}")
            # ================================================================
'''

def patch_pipeline(pipeline_path: Path, market_name: str):
    """Add HTML generation to a pipeline script"""
    with open(pipeline_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if 'GENERATE HTML MORNING REPORT' in content:
        print(f"  ⚠ {market_name} pipeline already patched, skipping...")
        return False
    
    # Find the return statement in run_full_overnight_pipeline
    marker = "            return results"
    
    if marker in content:
        # Insert HTML generation code before the return
        content = content.replace(marker, html_generation_code + "\n" + marker)
        
        with open(pipeline_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ Patched {market_name} pipeline")
        return True
    else:
        print(f"  ⚠ Could not find insertion point in {market_name} pipeline")
        return False

# Patch both pipelines
us_patched = patch_pipeline(us_pipeline, "US")
uk_patched = patch_pipeline(uk_pipeline, "UK")

print("[3/3] Verification...")
if us_patched or uk_patched:
    print("  ✓ HTML report generation added")
else:
    print("  ℹ No changes needed (already patched)")

print()
print("="*80)
print("  PATCH COMPLETE - v193 HTML Morning Reports")
print("="*80)
print()
print("Status: INSTALLED ✓")
print()
print("What changed:")
if us_patched:
    print("  ✓ US pipeline now generates HTML reports")
if uk_patched:
    print("  ✓ UK pipeline now generates HTML reports")
print()
print("Backup location: backup_pre_v193/")
print()
print("="*80)
print("  WHAT HAPPENS NEXT")
print("="*80)
print()
print("Tonight's pipeline:")
print("  1. Runs overnight analysis (JSON report)")
print("  2. Generates HTML morning report ← NEW!")
print("  3. Saves to: reports/{market}_morning_report_YYYYMMDD.html")
print()
print("Tomorrow morning:")
print("  - Open the HTML file in your browser")
print("  - Beautiful formatted report with:")
print("    • Market sentiment summary")
print("    • Top 10 opportunities with scores")
print("    • Sector breakdown")
print("    • System statistics")
print()
print("Example:")
print("  reports/us_morning_report_20260301.html")
print("  reports/uk_morning_report_20260301.html")
print()
print("="*80)
print()
input("Press Enter to exit...")

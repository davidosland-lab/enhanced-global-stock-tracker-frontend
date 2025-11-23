"""
Check Market Regime Engine Status
Diagnostic script to verify regime integration is working
"""

import sys
from pathlib import Path
import json

print("=" * 80)
print("MARKET REGIME ENGINE - STATUS CHECK")
print("=" * 80)
print()

# Check 1: Verify report_generator.py has regime code
print("CHECK 1: Report Generator Code")
print("-" * 80)
report_gen_path = Path(__file__).parent / 'models' / 'screening' / 'report_generator.py'
try:
    with open(report_gen_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_regime_param = 'event_risk_data: Dict = None' in content
    has_regime_method = 'def _build_market_regime_section' in content
    has_regime_call = 'regime_html = self._build_market_regime_section' in content
    
    print(f"✓ File exists: {report_gen_path}")
    print(f"{'✓' if has_regime_param else '✗'} Has event_risk_data parameter in generate_morning_report()")
    print(f"{'✓' if has_regime_method else '✗'} Has _build_market_regime_section() method")
    print(f"{'✓' if has_regime_call else '✗'} Calls _build_market_regime_section() in _build_html_report()")
    
    if has_regime_param and has_regime_method and has_regime_call:
        print("\n✅ Report generator has regime integration code")
    else:
        print("\n❌ Report generator is missing regime integration code")
        print("   → You may be using an old version of the code")
        print("   → Please extract the FIXED package: event_risk_guard_v1.3.20_REGIME_UI_FIXED_*.zip")
except Exception as e:
    print(f"✗ Error reading file: {e}")

print()

# Check 2: Verify overnight_pipeline.py passes event_risk_data
print("CHECK 2: Pipeline Integration")
print("-" * 80)
pipeline_path = Path(__file__).parent / 'models' / 'screening' / 'overnight_pipeline.py'
try:
    with open(pipeline_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check method signature
    has_param_in_sig = False
    for i, line in enumerate(lines):
        if 'def _generate_report' in line:
            # Check next few lines for parameter
            method_def = ''.join(lines[i:min(i+5, len(lines))])
            if 'event_risk_data: Dict = None' in method_def:
                has_param_in_sig = True
            break
    
    # Check method call
    has_param_in_call = False
    for line in lines:
        if 'self._generate_report' in line and 'event_risk_data' in line:
            has_param_in_call = True
            break
    
    print(f"✓ File exists: {pipeline_path}")
    print(f"{'✓' if has_param_in_sig else '✗'} _generate_report() has event_risk_data parameter")
    print(f"{'✓' if has_param_in_call else '✗'} _generate_report() is called with event_risk_data")
    
    if has_param_in_sig and has_param_in_call:
        print("\n✅ Pipeline passes event_risk_data correctly")
    else:
        print("\n❌ Pipeline is NOT passing event_risk_data")
        print("   → This is the bug that was fixed!")
        print("   → Please extract the FIXED package: event_risk_guard_v1.3.20_REGIME_UI_FIXED_*.zip")
except Exception as e:
    print(f"✗ Error reading file: {e}")

print()

# Check 3: Market Regime Engine availability
print("CHECK 3: Market Regime Engine Initialization")
print("-" * 80)
try:
    sys.path.insert(0, str(Path(__file__).parent / 'models'))
    from screening.event_risk_guard import EventRiskGuard
    
    print("✓ EventRiskGuard imported successfully")
    
    # Try to initialize
    guard = EventRiskGuard()
    print(f"✓ EventRiskGuard initialized")
    print(f"{'✓' if guard.regime_available else '✗'} Regime engine available: {guard.regime_available}")
    
    if guard.regime_available:
        print("\n✅ Market Regime Engine is available and initialized")
    else:
        print("\n⚠️  Market Regime Engine is NOT available")
        print("   → This is optional, but needed for regime display")
        print("   → Check if hmmlearn is installed: pip install hmmlearn")
except Exception as e:
    print(f"✗ Error initializing EventRiskGuard: {e}")
    print(f"   → Details: {type(e).__name__}: {e}")

print()

# Check 4: Recent reports
print("CHECK 4: Recent Reports")
print("-" * 80)
report_locations = [
    Path(__file__).parent / 'reports' / 'html',
    Path(__file__).parent / 'models' / 'screening' / 'reports' / 'morning_reports',
    Path(__file__).parent / 'models' / 'screening' / 'reports' / 'html'
]

found_reports = []
for loc in report_locations:
    if loc.exists():
        html_files = list(loc.glob('*.html'))
        if html_files:
            for f in html_files:
                found_reports.append((f, f.stat().st_mtime))

if found_reports:
    found_reports.sort(key=lambda x: x[1], reverse=True)
    latest = found_reports[0][0]
    print(f"✓ Found {len(found_reports)} report(s)")
    print(f"✓ Latest report: {latest.name}")
    
    # Check if it has regime section
    try:
        with open(latest, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_regime = 'Market Regime Analysis' in content or 'market regime' in content.lower()
        print(f"{'✓' if has_regime else '✗'} Latest report has regime section: {has_regime}")
        
        if not has_regime:
            print("\n⚠️  Report does NOT contain regime section")
            print("   → This report was generated with OLD code")
            print("   → Re-run the pipeline after extracting the FIXED package")
    except Exception as e:
        print(f"✗ Error reading report: {e}")
else:
    print("✗ No reports found")

print()

# Check 5: JSON data files
print("CHECK 5: JSON Data Files")
print("-" * 80)
json_locations = [
    Path(__file__).parent / 'reports' / 'html',
    Path(__file__).parent / 'models' / 'screening' / 'reports' / 'morning_reports',
    Path(__file__).parent / 'models' / 'screening' / 'reports' / 'html'
]

found_json = []
for loc in json_locations:
    if loc.exists():
        json_files = list(loc.glob('*_data.json'))
        if json_files:
            for f in json_files:
                found_json.append((f, f.stat().st_mtime))

if found_json:
    found_json.sort(key=lambda x: x[1], reverse=True)
    latest_json = found_json[0][0]
    print(f"✓ Found {len(found_json)} JSON file(s)")
    print(f"✓ Latest JSON: {latest_json.name}")
    
    # Check if it has regime data
    try:
        with open(latest_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        has_event_risk = 'event_risk_data' in data
        has_regime = False
        if has_event_risk and data['event_risk_data']:
            has_regime = 'market_regime' in data['event_risk_data']
        
        print(f"{'✓' if has_event_risk else '✗'} JSON has event_risk_data field: {has_event_risk}")
        print(f"{'✓' if has_regime else '✗'} JSON has market_regime data: {has_regime}")
        
        if has_regime:
            regime = data['event_risk_data']['market_regime']
            print(f"\n  Regime Label: {regime.get('regime_label', 'N/A')}")
            print(f"  Crash Risk: {regime.get('crash_risk_score', 0)*100:.1f}%")
            print(f"  Daily Vol: {regime.get('vol_1d', 0)*100:.2f}%")
    except json.JSONDecodeError:
        print("✗ JSON file is empty or malformed")
    except Exception as e:
        print(f"✗ Error reading JSON: {e}")
else:
    print("✗ No JSON data files found")

print()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("If you see ❌ or ✗ marks above, you need to:")
print()
print("1. Extract the FIXED deployment package:")
print("   event_risk_guard_v1.3.20_REGIME_UI_FIXED_20251121_030620.zip")
print()
print("2. Make sure you extract it to the correct location (overwriting old files)")
print()
print("3. Re-run the pipeline:")
print("   python models/screening/overnight_pipeline.py")
print()
print("4. Check the NEW report for the Market Regime Analysis section")
print()
print("5. Start the web UI to see regime data on dashboard:")
print("   python web_ui.py")
print()
print("=" * 80)

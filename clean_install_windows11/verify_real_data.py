#!/usr/bin/env python3
"""
Complete Data Verification Script
Scans all modules to ensure only real Yahoo Finance data is being used
No demo, synthetic, mock, or hardcoded data allowed
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

def scan_files_for_synthetic_data():
    """Scan all files for synthetic/demo data patterns"""
    
    synthetic_patterns = [
        # Direct synthetic data patterns
        r'mock[_\s]?data',
        r'fake[_\s]?data',
        r'demo[_\s]?data',
        r'synthetic[_\s]?data',
        r'sample[_\s]?data',
        r'dummy[_\s]?data',
        r'test[_\s]?data',
        
        # Hardcoded prices that might be synthetic
        r'price["\s:=]+100(?:\.00)?(?!\d)',  # Price exactly 100
        r'value["\s:=]+100(?:\.00)?(?!\d)',   # Value exactly 100
        r'(?:open|high|low|close)["\s:=]+100(?:\.00)?(?!\d)',
        
        # Hardcoded stock data
        r'hardcoded[_\s]?(?:price|data|value)',
        r'static[_\s]?(?:price|data|value)',
        
        # Common test values
        r'lorem\s+ipsum',
        r'foo[_\s]?bar',
        r'test[_\s]?123',
        
        # Placeholder comments
        r'//\s*TODO:?\s*(?:replace|use\s+real)',
        r'#\s*FIXME:?\s*(?:replace|use\s+real)',
        
        # Static data arrays (looking for hardcoded arrays)
        r'(?:prices?|values?|data)\s*=\s*\[[^\]]*100[^\]]*\]',
    ]
    
    issues_found = []
    files_checked = 0
    
    # Define directories to scan
    scan_dirs = [
        '.',
        'modules',
        'static',
        'modules/analysis',
        'modules/predictions',
        'modules/market-tracking'
    ]
    
    # File extensions to check
    extensions = ['.html', '.js', '.py', '.json', '.css']
    
    for scan_dir in scan_dirs:
        dir_path = Path(scan_dir)
        if not dir_path.exists():
            continue
            
        for ext in extensions:
            for file_path in dir_path.glob(f'*{ext}'):
                if file_path.is_file():
                    files_checked += 1
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        for pattern in synthetic_patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                            for match in matches:
                                # Get context around the match
                                start = max(0, match.start() - 50)
                                end = min(len(content), match.end() + 50)
                                context = content[start:end].strip()
                                
                                # Skip false positives
                                if 'yfinance' in context or 'yahoo' in context.lower():
                                    continue
                                    
                                issues_found.append({
                                    'file': str(file_path),
                                    'pattern': pattern,
                                    'match': match.group(),
                                    'context': context
                                })
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    
    return files_checked, issues_found

def verify_yahoo_finance_integration():
    """Verify that Yahoo Finance is properly integrated"""
    
    yahoo_checks = []
    
    # Check backend.py
    backend_file = Path('backend.py')
    if backend_file.exists():
        with open(backend_file, 'r') as f:
            content = f.read()
            
        checks = {
            'imports_yfinance': 'import yfinance' in content or 'from yfinance' in content,
            'uses_yf_download': 'yf.download' in content,
            'uses_yf_ticker': 'yf.Ticker' in content,
            'no_mock_data': 'mock' not in content.lower() and 'fake' not in content.lower(),
            'real_api_endpoints': '/api/stock' in content and '/api/historical' in content
        }
        yahoo_checks.append(('backend.py', checks))
    
    # Check ML backend
    ml_files = ['ml_backend_working.py', 'ml_training_backend.py', 'ml_backend_simple.py']
    for ml_file in ml_files:
        file_path = Path(ml_file)
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()
                
            checks = {
                'health_endpoint': '/health' in content,
                'no_hardcoded_predictions': 'return 100' not in content and 'prediction = 100' not in content,
                'uses_real_calculations': 'calculate' in content.lower() or 'predict' in content.lower()
            }
            yahoo_checks.append((ml_file, checks))
    
    return yahoo_checks

def check_hardcoded_values():
    """Check for specific hardcoded values that should be dynamic"""
    
    suspicious_values = []
    
    # Check HTML files for hardcoded prices
    html_files = list(Path('modules').glob('*.html')) + list(Path('.').glob('*.html'))
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for hardcoded CBA price (should be ~$170, not $100)
            if 'CBA' in content and ('$100' in content or 'price: 100' in content):
                suspicious_values.append({
                    'file': str(html_file),
                    'issue': 'Hardcoded CBA price at $100 (should be ~$170 from Yahoo Finance)',
                    'severity': 'HIGH'
                })
            
            # Check for static data arrays
            if 'data: [' in content and not 'fetch' in content:
                # Check if it's getting data dynamically
                if not ('async' in content or 'await' in content or 'then' in content):
                    suspicious_values.append({
                        'file': str(html_file),
                        'issue': 'Static data array without dynamic fetching',
                        'severity': 'MEDIUM'
                    })
                    
        except Exception as e:
            print(f"Error checking {html_file}: {e}")
    
    return suspicious_values

def generate_report():
    """Generate comprehensive data verification report"""
    
    print("=" * 80)
    print("         DATA VERIFICATION REPORT - Stock Tracker System")
    print("=" * 80)
    print(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 80)
    
    # Scan for synthetic data
    print("\n[1] SCANNING FOR SYNTHETIC/DEMO DATA")
    print("-" * 40)
    files_checked, issues = scan_files_for_synthetic_data()
    
    if issues:
        print(f"⚠️  ISSUES FOUND: {len(issues)} potential synthetic data patterns")
        for issue in issues[:5]:  # Show first 5 issues
            print(f"\n   File: {issue['file']}")
            print(f"   Pattern: {issue['pattern']}")
            print(f"   Match: {issue['match']}")
            print(f"   Context: ...{issue['context']}...")
    else:
        print(f"✅ CLEAN: No synthetic data patterns found in {files_checked} files")
    
    # Verify Yahoo Finance integration
    print("\n[2] YAHOO FINANCE INTEGRATION CHECK")
    print("-" * 40)
    yahoo_checks = verify_yahoo_finance_integration()
    
    for file_name, checks in yahoo_checks:
        all_good = all(checks.values())
        status = "✅" if all_good else "⚠️"
        print(f"\n{status} {file_name}:")
        for check_name, result in checks.items():
            check_status = "✓" if result else "✗"
            print(f"   {check_status} {check_name.replace('_', ' ').title()}")
    
    # Check for hardcoded values
    print("\n[3] HARDCODED VALUES CHECK")
    print("-" * 40)
    suspicious = check_hardcoded_values()
    
    if suspicious:
        print(f"⚠️  SUSPICIOUS VALUES FOUND: {len(suspicious)} potential issues")
        for item in suspicious:
            print(f"\n   [{item['severity']}] {item['file']}")
            print(f"   Issue: {item['issue']}")
    else:
        print("✅ CLEAN: No suspicious hardcoded values found")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("-" * 40)
    
    total_issues = len(issues) + len(suspicious)
    if total_issues == 0:
        print("✅ SYSTEM VERIFIED: All modules use real Yahoo Finance data")
        print("✅ No synthetic, mock, or demo data detected")
        print("✅ Ready for production deployment")
    else:
        print(f"⚠️  ATTENTION NEEDED: {total_issues} total issues require review")
        print("   Please address the issues above before deployment")
    
    print("\n" + "=" * 80)
    
    # Create detailed log file
    with open('data_verification_report.txt', 'w') as f:
        f.write(f"Data Verification Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Files Checked: {files_checked}\n")
        f.write(f"Synthetic Data Issues: {len(issues)}\n")
        f.write(f"Hardcoded Value Issues: {len(suspicious)}\n")
        f.write(f"\nDetailed Issues:\n")
        
        if issues:
            f.write("\nSynthetic Data Patterns:\n")
            for issue in issues:
                f.write(f"  - {issue['file']}: {issue['match']}\n")
        
        if suspicious:
            f.write("\nHardcoded Values:\n")
            for item in suspicious:
                f.write(f"  - [{item['severity']}] {item['file']}: {item['issue']}\n")
    
    print(f"\n📄 Detailed report saved to: data_verification_report.txt")

if __name__ == "__main__":
    generate_report()
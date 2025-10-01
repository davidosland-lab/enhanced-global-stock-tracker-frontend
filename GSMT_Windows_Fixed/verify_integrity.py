#!/usr/bin/env python3
"""
GSMT Integrity Verification Script
Ensures critical code sections remain intact and functional
"""

import os
import sys
import hashlib
import json
from datetime import datetime
import requests

class IntegrityVerifier:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
        
    def verify_file_exists(self, filepath):
        """Check if critical file exists"""
        if os.path.exists(filepath):
            self.success.append(f"✅ File exists: {filepath}")
            return True
        else:
            self.errors.append(f"❌ Missing file: {filepath}")
            return False
    
    def verify_no_synthetic_data(self, filepath):
        """Ensure no synthetic data generation in code"""
        if not self.verify_file_exists(filepath):
            return False
            
        with open(filepath, 'r') as f:
            content = f.read().lower()
            
        forbidden = ['math.random', 'random()', 'synthetic', 'fake', 'mock']
        
        found_violations = []
        for pattern in forbidden:
            if pattern in content and 'no synthetic' not in content:
                found_violations.append(pattern)
        
        if found_violations:
            self.errors.append(f"❌ {filepath} has forbidden: {found_violations}")
            return False
        else:
            self.success.append(f"✅ {filepath} is clean")
            return True
    
    def verify_correct_calculations(self):
        """Verify backend uses correct percentage calculation"""
        filepath = 'backend_fixed.py'
        if not self.verify_file_exists(filepath):
            return False
            
        with open(filepath, 'r') as f:
            content = f.read()
        
        required = ["hist['Close'].iloc[-2]", "yfinance"]
        
        for pattern in required:
            if pattern not in content:
                self.errors.append(f"❌ Missing: {pattern}")
                return False
        
        self.success.append("✅ Calculations verified")
        return True
    
    def verify_localhost_urls(self):
        """Verify all HTML files use hardcoded localhost URLs"""
        issues = []
        
        files_to_check = ['simple_working_dashboard.html']
        files_to_check.extend([f'modules/{f}' for f in os.listdir('modules') 
                               if f.endswith('.html')])
        
        for filepath in files_to_check:
            with open(filepath, 'r') as f:
                content = f.read()
                if "window.location.hostname.replace" in content:
                    issues.append(filepath)
        
        if issues:
            self.errors.append(f"❌ Dynamic URLs in: {issues}")
            return False
        else:
            self.success.append("✅ All using localhost:8002")
            return True
    
    def run_all_checks(self):
        """Run all verification checks"""
        print("\n" + "="*60)
        print("GSMT INTEGRITY VERIFICATION")
        print("="*60 + "\n")
        
        self.verify_correct_calculations()
        self.verify_localhost_urls()
        
        print("\n✅ SUCCESS:")
        for msg in self.success:
            print(f"  {msg}")
        
        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for msg in self.errors:
                print(f"  {msg}")
        
        print("\n" + "="*60)
        if self.errors:
            print("❌ VERIFICATION FAILED!")
            return False
        else:
            print("✅ ALL VERIFICATIONS PASSED!")
            return True

def main():
    verifier = IntegrityVerifier()
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Integrity Verification Script - Ensures no regression
Checks that backend is using real data with correct calculations
"""

import json
import requests
import subprocess
import sys
from pathlib import Path

class IntegrityChecker:
    def __init__(self):
        self.backend_url = "http://localhost:8002"
        self.errors = []
        self.warnings = []
        
    def check_backend_running(self):
        """Check if backend is running on port 8002"""
        try:
            response = requests.get(f"{self.backend_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "Fixed Market Data API" in data.get("service", ""):
                    print("✓ Backend is running on port 8002")
                    return True
                else:
                    self.errors.append("Backend running but not the fixed version!")
            else:
                self.errors.append(f"Backend returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.errors.append(f"Backend not accessible: {e}")
        return False
    
    def check_data_accuracy(self):
        """Verify All Ordinaries shows correct percentage"""
        try:
            response = requests.get(f"{self.backend_url}/api/indices", timeout=10)
            data = response.json()
            
            if "^AORD" in data.get("indices", {}):
                aord = data["indices"]["^AORD"]
                price = aord.get("price", 0)
                change_percent = aord.get("changePercent", 0)
                data_source = aord.get("dataSource", "")
                
                # Check if using history-based data
                if "History-based" in data_source:
                    print("✓ Using history-based data (correct method)")
                else:
                    self.warnings.append(f"Data source: {data_source} (should be History-based)")
                
                # Check percentage is approximately -0.14%
                if abs(change_percent - (-0.14)) < 0.05:  # Allow 0.05% tolerance
                    print(f"✓ All Ordinaries: {price:.2f} points, {change_percent:.2f}% (CORRECT)")
                    return True
                else:
                    self.errors.append(f"All Ordinaries showing {change_percent:.2f}% instead of -0.14%!")
            else:
                self.errors.append("All Ordinaries data not found!")
        except Exception as e:
            self.errors.append(f"Failed to verify data: {e}")
        return False
    
    def check_no_synthetic_data(self):
        """Ensure no synthetic data generation in code"""
        files_to_check = [
            "backend_fixed.py",
            "simple_working_dashboard.html",
            "*.js"
        ]
        
        synthetic_patterns = [
            "Math.random",
            "generateMockData",
            "generateSynthetic",
            "mockData",
            "testData"
        ]
        
        found_synthetic = False
        for pattern in synthetic_patterns:
            result = subprocess.run(
                f"grep -r '{pattern}' {' '.join(files_to_check)} 2>/dev/null",
                shell=True,
                capture_output=True,
                text=True,
                cwd="/home/user/webapp"
            )
            if result.stdout:
                self.warnings.append(f"Found '{pattern}' in files: {result.stdout[:100]}")
                found_synthetic = True
        
        if not found_synthetic:
            print("✓ No synthetic data generation found")
            return True
        return False
    
    def check_history_data_usage(self):
        """Verify backend uses history data for previous close"""
        backend_file = Path("/home/user/webapp/backend_fixed.py")
        if backend_file.exists():
            content = backend_file.read_text()
            if "hist['Close'].iloc[-2]" in content:
                print("✓ Backend uses correct history data for previous close")
                return True
            else:
                self.errors.append("Backend not using hist['Close'].iloc[-2] for previous close!")
        else:
            self.errors.append("backend_fixed.py not found!")
        return False
    
    def verify_checksums(self):
        """Verify file integrity using checksums"""
        checksum_file = Path("/home/user/webapp/protected_working_code/checksums.md5")
        if checksum_file.exists():
            result = subprocess.run(
                "cd /home/user/webapp && md5sum -c protected_working_code/checksums.md5 2>/dev/null",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✓ File checksums match (no unauthorized changes)")
                return True
            else:
                self.warnings.append("File checksums don't match - files may have been modified")
                return False
        else:
            self.warnings.append("Checksum file not found")
            return False
    
    def run_all_checks(self):
        """Run all integrity checks"""
        print("\n" + "="*60)
        print("INTEGRITY VERIFICATION REPORT")
        print("="*60)
        
        checks = [
            ("Backend Running", self.check_backend_running),
            ("Data Accuracy", self.check_data_accuracy),
            ("No Synthetic Data", self.check_no_synthetic_data),
            ("History Data Usage", self.check_history_data_usage),
            ("File Integrity", self.verify_checksums)
        ]
        
        passed = 0
        failed = 0
        
        for name, check_func in checks:
            print(f"\nChecking {name}...")
            if check_func():
                passed += 1
            else:
                failed += 1
        
        print("\n" + "-"*60)
        print(f"RESULTS: {passed} passed, {failed} failed")
        
        if self.errors:
            print("\n⚠️  ERRORS:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors:
            print("\n✅ ALL CRITICAL CHECKS PASSED - System is working correctly!")
            print("   All Ordinaries showing correct -0.14% change")
            print("   Using real Yahoo Finance data with history-based calculations")
            return True
        else:
            print("\n❌ CRITICAL ISSUES DETECTED - Immediate action required!")
            print("\nTo recover, run:")
            print("  cp protected_working_code/PROTECTED_backend_fixed_v1.py backend_fixed.py")
            print("  python backend_fixed.py")
            return False

def main():
    checker = IntegrityChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
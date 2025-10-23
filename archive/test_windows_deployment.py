#!/usr/bin/env python3
"""
Windows 11 Deployment Simulator
Tests GSMT deployment as it would run on Windows 11
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path

class Windows11DeploymentTest:
    def __init__(self):
        self.test_results = []
        self.errors = []
        self.base_path = Path.cwd()
        
    def log(self, message, status="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
        self.test_results.append({"time": timestamp, "status": status, "message": message})
    
    def test_file_structure(self):
        """Test 1: Verify all files exist"""
        self.log("Testing file structure...", "TEST")
        
        required_files = [
            "backend_fixed.py",
            "simple_working_dashboard.html",
            "requirements.txt",
            "FIX_WINDOWS_URLS.ps1",
            "verify_integrity.py",
            "RECOVERY_FRAMEWORK.md",
            "modules/global_indices_tracker.html",
            "modules/single_stock_tracker.html",
            "modules/cba_analysis.html",
            "modules/technical_analysis.html",
            "modules/ml_predictions.html",
            "modules/document_center.html"
        ]
        
        all_exist = True
        for file in required_files:
            filepath = self.base_path / file
            if filepath.exists():
                self.log(f"✅ Found: {file}", "PASS")
            else:
                self.log(f"❌ Missing: {file}", "FAIL")
                all_exist = False
                
        return all_exist
    
    def test_url_configuration(self):
        """Test 2: Verify localhost URLs are configured"""
        self.log("Testing URL configuration...", "TEST")
        
        files_to_check = [
            "simple_working_dashboard.html",
            "modules/global_indices_tracker.html",
            "modules/single_stock_tracker.html",
            "modules/cba_analysis.html",
            "modules/technical_analysis.html",
            "modules/ml_predictions.html"
        ]
        
        all_correct = True
        for file in files_to_check:
            filepath = self.base_path / file
            if filepath.exists():
                with open(filepath, 'r') as f:
                    content = f.read()
                    if "'http://localhost:8002'" in content:
                        self.log(f"✅ {file}: Using localhost:8002", "PASS")
                    elif "window.location.hostname.replace" in content:
                        self.log(f"❌ {file}: Still using dynamic URL", "FAIL")
                        all_correct = False
                    else:
                        self.log(f"⚠️ {file}: No API URL found", "WARN")
        
        return all_correct
    
    def test_backend_api(self):
        """Test 3: Verify backend API is accessible"""
        self.log("Testing backend API...", "TEST")
        
        try:
            # Test root endpoint
            response = requests.get("http://localhost:8002/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "active":
                    self.log("✅ Backend API is active", "PASS")
                else:
                    self.log("⚠️ Backend API response unexpected", "WARN")
            else:
                self.log(f"❌ Backend returned status {response.status_code}", "FAIL")
                return False
                
            # Test indices endpoint
            response = requests.get("http://localhost:8002/api/indices", timeout=10)
            if response.status_code == 200:
                data = response.json()
                indices = data.get("indices", {})
                
                # Check for All Ordinaries
                if "^AORD" in indices:
                    aord = indices["^AORD"]
                    price = aord.get("price", 0)
                    change_percent = aord.get("changePercent", 0)
                    
                    self.log(f"✅ All Ordinaries: {price:.2f} ({change_percent:.2f}%)", "PASS")
                    
                    # Verify it's real data (not synthetic)
                    if price > 8000 and price < 10000:  # Reasonable range
                        self.log("✅ Data appears to be real (within expected range)", "PASS")
                    else:
                        self.log("⚠️ Data might be synthetic or incorrect", "WARN")
                else:
                    self.log("❌ No All Ordinaries data found", "FAIL")
                    return False
            else:
                self.log(f"❌ Indices API returned status {response.status_code}", "FAIL")
                return False
                
            return True
            
        except requests.exceptions.ConnectionError:
            self.log("❌ Cannot connect to backend (not running?)", "FAIL")
            return False
        except Exception as e:
            self.log(f"❌ API test failed: {e}", "FAIL")
            return False
    
    def test_no_synthetic_data(self):
        """Test 4: Verify no synthetic data in code"""
        self.log("Testing for synthetic data...", "TEST")
        
        files_to_check = ["backend_fixed.py", "simple_working_dashboard.html"]
        
        forbidden_patterns = ["Math.random", "random()", "mock", "fake"]
        
        all_clean = True
        for file in files_to_check:
            filepath = self.base_path / file
            if filepath.exists():
                with open(filepath, 'r') as f:
                    content = f.read().lower()
                    
                found_issues = []
                for pattern in forbidden_patterns:
                    if pattern.lower() in content:
                        # Check for exceptions
                        if pattern == "random" and "no random" in content:
                            continue
                        found_issues.append(pattern)
                
                if found_issues:
                    self.log(f"❌ {file} contains: {found_issues}", "FAIL")
                    all_clean = False
                else:
                    self.log(f"✅ {file} is clean", "PASS")
        
        return all_clean
    
    def test_windows_compatibility(self):
        """Test 5: Check Windows-specific compatibility"""
        self.log("Testing Windows compatibility...", "TEST")
        
        # Check for Windows line endings in batch files
        batch_files = ["START_GSMT_WINDOWS_FIXED.bat"]
        
        for file in batch_files:
            filepath = self.base_path / file
            if filepath.exists():
                with open(filepath, 'rb') as f:
                    content = f.read()
                    if b'\r\n' in content:
                        self.log(f"✅ {file} has Windows line endings", "PASS")
                    else:
                        self.log(f"⚠️ {file} might need CRLF conversion", "WARN")
        
        # Check Python shebang compatibility
        py_files = ["backend_fixed.py", "verify_integrity.py"]
        for file in py_files:
            filepath = self.base_path / file
            if filepath.exists():
                with open(filepath, 'r') as f:
                    first_line = f.readline()
                    if first_line.startswith("#!"):
                        self.log(f"✅ {file} has shebang (will work with python command)", "PASS")
        
        return True
    
    def simulate_windows_deployment(self):
        """Simulate full Windows deployment"""
        self.log("="*60, "INFO")
        self.log("WINDOWS 11 DEPLOYMENT SIMULATION", "INFO")
        self.log("="*60, "INFO")
        
        # Run all tests
        tests = [
            ("File Structure", self.test_file_structure),
            ("URL Configuration", self.test_url_configuration),
            ("Backend API", self.test_backend_api),
            ("No Synthetic Data", self.test_no_synthetic_data),
            ("Windows Compatibility", self.test_windows_compatibility)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            self.log(f"\\nRunning: {test_name}", "INFO")
            result = test_func()
            if not result:
                all_passed = False
        
        # Generate report
        self.log("\\n" + "="*60, "INFO")
        self.log("DEPLOYMENT TEST SUMMARY", "INFO")
        self.log("="*60, "INFO")
        
        if all_passed:
            self.log("✅ ALL TESTS PASSED - Ready for Windows 11 deployment!", "PASS")
            self.log("\\nNext steps for Windows 11:", "INFO")
            self.log("1. Copy GSMT_Windows_Fixed_v2.0.zip to Windows machine", "INFO")
            self.log("2. Extract to C:\\GSMT\\", "INFO")
            self.log("3. Run FIX_WINDOWS_URLS.ps1 in PowerShell", "INFO")
            self.log("4. Run START_GSMT_WINDOWS_FIXED.bat", "INFO")
            self.log("5. Access dashboard at http://localhost:8080", "INFO")
        else:
            self.log("❌ SOME TESTS FAILED - Review issues before deployment", "FAIL")
            self.log("\\nIssues to fix:", "INFO")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    self.log(f"  - {result['message']}", "INFO")
        
        return all_passed

def main():
    tester = Windows11DeploymentTest()
    success = tester.simulate_windows_deployment()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
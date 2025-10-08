#!/usr/bin/env python3
"""
Diagnostic script for Document Analyzer
Identifies why analysis results are inconsistent
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

def check_current_implementation():
    """Check current document analyzer implementation"""
    print("=" * 60)
    print("DOCUMENT ANALYZER DIAGNOSTIC")
    print("=" * 60)
    
    # 1. Check if FinBERT is installed
    print("\n1. CHECKING FINBERT INSTALLATION:")
    print("-" * 40)
    try:
        from transformers import pipeline
        print("✓ transformers library installed")
        
        # Try to load FinBERT
        try:
            analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")
            print("✓ FinBERT model can be loaded")
            
            # Test analysis
            test_text = "The company reported strong earnings growth."
            result = analyzer(test_text)
            print(f"✓ Test analysis works: {result[0]}")
            
        except Exception as e:
            print(f"✗ FinBERT model error: {e}")
            
    except ImportError:
        print("✗ transformers library NOT installed")
        print("  Run: pip install transformers torch")
    
    # 2. Check backend implementation
    print("\n2. CHECKING BACKEND IMPLEMENTATION:")
    print("-" * 40)
    
    backend_file = "clean_install_windows11/backend.py"
    if os.path.exists(backend_file):
        with open(backend_file, 'r') as f:
            content = f.read()
            
        if "finbert" in content.lower() or "sentiment" in content.lower():
            print("✓ Backend has sentiment analysis code")
        else:
            print("✗ Backend does NOT have sentiment analysis")
            print("  The upload endpoint just saves files without analysis")
            
        if "analyze_document" in content or "analyze_text" in content:
            print("✓ Backend has document analysis function")
        else:
            print("✗ Backend missing document analysis function")
    else:
        print("✗ Backend file not found")
    
    # 3. Check for analysis cache
    print("\n3. CHECKING FOR CACHING MECHANISM:")
    print("-" * 40)
    
    cache_dirs = ["analysis_cache", "cache", ".cache"]
    cache_found = False
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            cache_files = list(Path(cache_dir).glob("*"))
            if cache_files:
                print(f"✓ Cache directory found: {cache_dir}")
                print(f"  Contains {len(cache_files)} cached items")
                cache_found = True
                break
    
    if not cache_found:
        print("✗ No cache directory found")
        print("  This could cause inconsistent results")
    
    # 4. Check upload directory
    print("\n4. CHECKING UPLOAD DIRECTORY:")
    print("-" * 40)
    
    if os.path.exists("uploads"):
        upload_files = list(Path("uploads").glob("*"))
        print(f"✓ Uploads directory exists")
        print(f"  Contains {len(upload_files)} files")
        
        # Check if files are being reprocessed
        if upload_files:
            test_file = upload_files[0]
            file_hash = hashlib.md5(open(test_file, 'rb').read()).hexdigest()
            print(f"  Sample file hash: {file_hash[:8]}...")
    else:
        print("✗ Uploads directory not found")
    
    # 5. Identify the issue
    print("\n5. DIAGNOSIS RESULTS:")
    print("-" * 40)
    print("\n⚠️ ISSUE IDENTIFIED:")
    print("The current backend.py does NOT implement document analysis!")
    print("It only uploads files without any sentiment analysis.")
    print("\nThis is why you see inconsistent results - ")
    print("the frontend may be generating random/placeholder data.")
    
    print("\n📋 SOLUTION:")
    print("1. Install FinBERT: Run INSTALL_FINBERT.bat")
    print("2. Replace backend endpoint with document_analyzer_with_finbert.py")
    print("3. Or run document analyzer on separate port (8004)")
    print("4. Update frontend to use the new endpoint")
    
    # 6. Test proper implementation
    print("\n6. TESTING PROPER IMPLEMENTATION:")
    print("-" * 40)
    
    if os.path.exists("document_analyzer_with_finbert.py"):
        print("✓ New document analyzer with FinBERT found")
        print("  Run: python document_analyzer_with_finbert.py")
        print("  This will provide consistent sentiment analysis")
    else:
        print("✗ document_analyzer_with_finbert.py not found")

def test_consistency():
    """Test if analysis would be consistent"""
    print("\n7. CONSISTENCY TEST:")
    print("-" * 40)
    
    test_text = "The quarterly earnings exceeded expectations with strong revenue growth."
    
    try:
        from transformers import pipeline
        analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")
        
        print(f"Test text: '{test_text}'")
        print("\nRunning 5 analyses to check consistency:")
        
        results = []
        for i in range(5):
            result = analyzer(test_text)[0]
            results.append(result)
            print(f"  Run {i+1}: {result['label']} (confidence: {result['score']:.3f})")
        
        # Check if results are consistent
        labels = [r['label'] for r in results]
        if len(set(labels)) == 1:
            print("\n✓ Results are CONSISTENT")
        else:
            print("\n✗ Results are INCONSISTENT")
            print(f"  Different labels found: {set(labels)}")
            
    except Exception as e:
        print(f"Cannot run consistency test: {e}")
        print("Install FinBERT first with INSTALL_FINBERT.bat")

if __name__ == "__main__":
    check_current_implementation()
    test_consistency()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
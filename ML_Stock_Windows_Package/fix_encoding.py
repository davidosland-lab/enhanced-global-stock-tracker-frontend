#!/usr/bin/env python3
"""
Fix UTF-8 Encoding Issues
Diagnose and fix file encoding problems that prevent server startup
"""

import os
import sys
import chardet
import codecs

print("="*70)
print("   UTF-8 ENCODING FIX TOOL")
print("="*70)
print()

def check_file_encoding(filepath):
    """Check the encoding of a file"""
    try:
        # Try to detect encoding
        with open(filepath, 'rb') as f:
            raw = f.read(10000)  # Read first 10KB
            result = chardet.detect(raw)
            encoding = result['encoding']
            confidence = result['confidence']
            
        # Check for BOM
        has_bom = False
        if raw.startswith(codecs.BOM_UTF8):
            has_bom = True
            print(f"   ⚠️ UTF-8 BOM detected")
        elif raw.startswith(codecs.BOM_UTF16):
            has_bom = True
            print(f"   ⚠️ UTF-16 BOM detected")
        
        return encoding, confidence, has_bom
    except Exception as e:
        return None, 0, False

def fix_file_encoding(filepath, target_encoding='utf-8'):
    """Convert file to UTF-8 without BOM"""
    try:
        # Detect current encoding
        encoding, confidence, has_bom = check_file_encoding(filepath)
        
        if encoding is None:
            print(f"   ❌ Cannot detect encoding for {filepath}")
            return False
        
        print(f"   Detected: {encoding} (confidence: {confidence:.1%})")
        
        # Read with detected encoding
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
        except:
            # Try with UTF-8 ignoring errors
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        # Remove BOM if present
        if content.startswith('\ufeff'):
            content = content[1:]
            print(f"   ✅ Removed BOM")
        
        # Write back as UTF-8 without BOM
        backup_path = filepath + '.backup'
        os.rename(filepath, backup_path)
        
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print(f"   ✅ Converted to UTF-8 (backup: {os.path.basename(backup_path)})")
        return True
        
    except Exception as e:
        print(f"   ❌ Error fixing {filepath}: {e}")
        return False

def scan_python_files():
    """Scan all Python files for encoding issues"""
    print("Scanning Python files for encoding issues...\n")
    
    issues_found = []
    files_fixed = []
    
    # List of Python files to check
    python_files = [
        'server.py',
        'server_minimal.py',
        'unified_production_server.py',
        'server_fixed_crumb.py',
        'test_server.py',
        'diagnose_server.py',
        'diagnostics.py'
    ]
    
    for filename in python_files:
        if os.path.exists(filename):
            print(f"Checking: {filename}")
            
            encoding, confidence, has_bom = check_file_encoding(filename)
            
            if encoding and encoding.lower() != 'utf-8' or has_bom:
                print(f"   ⚠️ Issue found: {encoding} encoding" + (" with BOM" if has_bom else ""))
                issues_found.append(filename)
                
                # Ask to fix
                response = input(f"   Fix this file? (y/n): ").lower()
                if response == 'y':
                    if fix_file_encoding(filename):
                        files_fixed.append(filename)
            else:
                print(f"   ✅ OK: UTF-8 encoding")
    
    print("\n" + "="*70)
    print("SCAN COMPLETE")
    print("="*70)
    
    if issues_found:
        print(f"\n⚠️ Found {len(issues_found)} file(s) with encoding issues:")
        for f in issues_found:
            print(f"   • {f}")
    
    if files_fixed:
        print(f"\n✅ Fixed {len(files_fixed)} file(s):")
        for f in files_fixed:
            print(f"   • {f}")
    
    if not issues_found:
        print("\n✅ No encoding issues found in Python files!")
    
    return issues_found, files_fixed

def create_clean_server():
    """Create a clean UTF-8 test server"""
    print("\nCreating clean UTF-8 test server...")
    
    server_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean UTF-8 Test Server"""

import sys
import os

print("Starting clean server...")
print(f"Python: {sys.version}")
print(f"Default encoding: {sys.getdefaultencoding()}")
print(f"File system encoding: {sys.getfilesystemencoding()}")

try:
    from flask import Flask, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route("/")
    def index():
        return """
        <html>
        <head><title>Clean Test Server</title></head>
        <body>
            <h1>Clean UTF-8 Server Working!</h1>
            <p>This server has no encoding issues.</p>
        </body>
        </html>
        """
    
    @app.route("/api/test")
    def test():
        return jsonify({"status": "ok", "encoding": "utf-8"})
    
    if __name__ == "__main__":
        print("Server starting on http://localhost:8000")
        app.run(host="127.0.0.1", port=8000, debug=False)
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Install with: pip install flask flask-cors")
except Exception as e:
    print(f"Error: {e}")
'''
    
    # Write with proper UTF-8 encoding
    with open('clean_test_server.py', 'w', encoding='utf-8', newline='\n') as f:
        f.write(server_code)
    
    print("✅ Created clean_test_server.py")
    return True

def main():
    """Main function"""
    print("This tool will fix UTF-8 encoding issues that prevent server startup\n")
    
    # Check if chardet is installed
    try:
        import chardet
    except ImportError:
        print("Installing chardet for encoding detection...")
        os.system("pip install chardet")
        import chardet
    
    # Scan for issues
    issues, fixed = scan_python_files()
    
    # Create clean server
    print("\n" + "="*70)
    response = input("\nCreate a clean UTF-8 test server? (y/n): ").lower()
    if response == 'y':
        create_clean_server()
        print("\nYou can now test with:")
        print("   python clean_test_server.py")
    
    print("\n" + "="*70)
    print("ENCODING FIX COMPLETE")
    print("="*70)
    
    if fixed:
        print("\n✅ Files have been fixed. Try running the server again.")
    else:
        print("\n💡 TIP: If you still get encoding errors:")
        print("   1. Use clean_test_server.py")
        print("   2. Check for non-ASCII characters in your files")
        print("   3. Ensure all files are saved as UTF-8 without BOM")

if __name__ == '__main__':
    main()
    print("\nPress Enter to exit...")
    input()
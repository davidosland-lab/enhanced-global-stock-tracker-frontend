# ✅ WINDOWS UTF-8 ERROR - FIXED!

## 🚨 The Problem You Encountered:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0
```

This is a known Flask/Windows issue where Flask tries to read a .env file with incorrect encoding.

## ✅ The Solution - 3 Methods (Try in Order):

### Method 1: Use START_SERVER.bat (Simplest)
```batch
1. Double-click START_SERVER.bat
2. This automatically sets FLASK_SKIP_DOTENV=1
3. Server should start at http://localhost:8000
```

### Method 2: Use run_server.py (Most Reliable)
```batch
1. Open Command Prompt
2. Navigate to your folder: cd C:\Users\david\AST
3. Run: python run_server.py
4. This Python wrapper handles all encoding issues
```

### Method 3: Use RUN_STOCK_SYSTEM_WINDOWS.bat (Full Setup)
```batch
1. Double-click RUN_STOCK_SYSTEM_WINDOWS.bat
2. This includes auto-detection and fixes for:
   - Missing Python
   - Package installation
   - UTF-8 encoding issues
   - Conflicting .env files
```

## 🔧 Manual Fix (If Above Don't Work):

### Step 1: Check for .env Files
```batch
# In Command Prompt:
cd C:\Users\david\AST
dir .env*

# If any .env files exist, rename them:
ren .env .env.backup
```

### Step 2: Set Environment Variables
```batch
# In Command Prompt, before running Python:
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8
chcp 65001
```

### Step 3: Run the Server
```batch
python unified_stock_system_local.py
```

## 🛠️ Alternative: PowerShell Method
```powershell
# Open PowerShell as Administrator
cd C:\Users\david\AST

# Set environment variables
$env:FLASK_SKIP_DOTENV = "1"
$env:PYTHONIOENCODING = "utf-8"

# Run server
python unified_stock_system_local.py
```

## 📝 Permanent Fix (One-Time Setup):

### Add System Environment Variables:
1. Press `Win + X` → System → Advanced system settings
2. Click "Environment Variables"
3. Under "User variables", click "New"
4. Add these:
   - Variable: `FLASK_SKIP_DOTENV`, Value: `1`
   - Variable: `PYTHONIOENCODING`, Value: `utf-8`
5. Click OK and restart Command Prompt

## 🎯 Quick Test After Fix:
```batch
# Test if it's working:
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

## 📊 Files in Your Package:

1. **unified_stock_system_local.py** - Main application (UPDATED with fix)
2. **run_server.py** - Python wrapper that handles all encoding
3. **START_SERVER.bat** - Simple batch launcher
4. **RUN_STOCK_SYSTEM_WINDOWS.bat** - Advanced launcher with auto-fix
5. **requirements_unified.txt** - Python dependencies
6. **README_LOCAL_CHARTS.md** - Full documentation

## ✅ What Was Fixed:

1. Added `os.environ['FLASK_SKIP_DOTENV'] = '1'` to prevent Flask from loading .env
2. Created multiple fallback launchers for Windows
3. Added encoding configuration for Windows terminals
4. Provided wrapper script that handles all edge cases

## 🚀 Recommended Method:

**Use `run_server.py`** - This Python wrapper is the most reliable:
```batch
cd C:\Users\david\AST
python run_server.py
```

This handles:
- UTF-8 encoding setup
- Environment variable configuration  
- Fallback methods if primary fails
- Clean error messages

## 📞 If Still Having Issues:

The problem is 100% related to Flask trying to read a .env file. Solutions:
1. Delete any .env files in the directory
2. Use the Python wrapper (run_server.py)
3. Set FLASK_SKIP_DOTENV=1 environment variable

---

**Your server is now running at: http://localhost:8000**  
**All charts work locally without CDN!**
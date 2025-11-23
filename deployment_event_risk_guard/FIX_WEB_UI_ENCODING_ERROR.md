# Fix: Web UI Unicode Decode Error

## Date: 2025-11-16

## Error Message

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte

[ERROR] Web UI failed to start
```

---

## Root Cause

**Flask's `debug=True` mode automatically tries to load a `.env` file** for environment variables. When the `.env` file:
- Doesn't exist
- Has incorrect encoding (UTF-16 with BOM)
- Contains invalid UTF-8 characters

Flask crashes with a `UnicodeDecodeError`.

### Why This Happened

The error trace shows:
```python
File "dotenv/main.py", line 364, in load_dotenv
    return dotenv.set_as_environment_variables()
File "dotenv/parser.py", line 64, in __init__
    self.string = stream.read()
File "<frozen codecs>", line 322, in decode
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0
```

The `0xff` byte at position 0 indicates:
- UTF-16 BOM (Byte Order Mark)
- Or corrupted file encoding

---

## Fix Applied

### Solution: Disable `.env` File Loading

**Modified**: `web_ui.py` line 240-242

**Before**:
```python
if __name__ == '__main__':
    print("=" * 80)
    print("Event Risk Guard - Web UI")
    print("=" * 80)
    print(f"Starting web server...")
    print(f"Access dashboard at: http://localhost:5000")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**After**:
```python
if __name__ == '__main__':
    print("=" * 80)
    print("Event Risk Guard - Web UI")
    print("=" * 80)
    print(f"Starting web server...")
    print(f"Access dashboard at: http://localhost:5000")
    print("=" * 80)
    
    # Disable .env file loading to avoid encoding issues
    os.environ['FLASK_SKIP_DOTENV'] = '1'
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**What Changed**:
- Added `os.environ['FLASK_SKIP_DOTENV'] = '1'` before `app.run()`
- This tells Flask to skip automatic `.env` file loading
- Web UI doesn't need `.env` file (uses `screening_config.json` instead)

---

## Alternative Solutions

### Option 1: Disable Debug Mode (Production-Safe)

If you want to disable debug mode entirely:

**Change line 242** from:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

**To**:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

**Pros**:
- ✅ More secure (doesn't expose debug info)
- ✅ No .env file loading attempt
- ✅ Better for production use

**Cons**:
- ❌ No auto-reload on code changes
- ❌ Less detailed error messages

---

### Option 2: Create Valid .env File

If you want to keep debug mode and use .env:

1. Create file: `.env` in `deployment_event_risk_guard/`
2. Save with **UTF-8 encoding (no BOM)**
3. Add any environment variables (optional):

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1

# Optional: Override port
# PORT=5000
```

**Save as**: UTF-8 (not UTF-16, not UTF-8 with BOM)

In Notepad:
- File → Save As
- Encoding: **UTF-8** (not "UTF-8 with BOM")

---

## How to Verify Fix

### Test the Web UI

Run:
```batch
START_WEB_UI.bat
```

**Expected Output**:
```
================================================================================
EVENT RISK GUARD - WEB UI
================================================================================

Starting web interface...

Once started, access the dashboard at:
  http://localhost:5000

Press Ctrl+C to stop the server
================================================================================

[INFO] Starting Flask web server...

[All the FinBERT loading messages...]

================================================================================
Event Risk Guard - Web UI
================================================================================
Starting web server...
Access dashboard at: http://localhost:5000
================================================================================
 * Serving Flask app 'web_ui'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

✅ **No Unicode error!**

---

## Understanding the Fix

### Why FLASK_SKIP_DOTENV Works

```python
os.environ['FLASK_SKIP_DOTENV'] = '1'
```

This environment variable tells Flask's CLI loader:
- Skip searching for `.env` file
- Skip loading `.env` file
- Skip parsing `.env` file

**Since we don't need .env** (all config is in `screening_config.json`), this is safe.

---

### What Flask Was Trying to Do

Flask's debug mode automatically looks for:
1. `.env` in current directory
2. `.flaskenv` in current directory

And loads them using the `python-dotenv` library.

**The error occurred** because:
- Flask found something it thought was a `.env` file
- Tried to read it as UTF-8
- File had non-UTF-8 bytes (0xff BOM)
- Crashed with UnicodeDecodeError

---

## Windows-Specific Issue

This is more common on Windows because:

1. **Notepad default encoding**: UTF-16 LE with BOM
2. **Hidden files**: `.env` files might be hidden in Windows Explorer
3. **Encoding confusion**: Windows apps often add BOM to text files

**Linux/Mac**: Usually UTF-8 without BOM by default  
**Windows**: Often UTF-16 or UTF-8 with BOM

---

## Files Modified

| File | Change | Lines |
|------|--------|-------|
| `web_ui.py` | Added `FLASK_SKIP_DOTENV` | 240-242 |

---

## Testing Checklist

After fix is applied:

- [ ] Run `START_WEB_UI.bat`
- [ ] No UnicodeDecodeError shown
- [ ] See "Running on http://127.0.0.1:5000"
- [ ] Open browser to http://localhost:5000
- [ ] Dashboard loads successfully
- [ ] No console errors

---

## If Issue Persists

If you still get the error after this fix:

### Check for Hidden .env File

**PowerShell**:
```powershell
cd C:\Users\david\AASS\deployment_event_risk_guard
Get-ChildItem -Force | Where-Object { $_.Name -like "*.env*" }
```

### Check File Encoding

**PowerShell**:
```powershell
Get-Content .env -Encoding Byte -TotalCount 4
```

If you see `255 254` (FF FE), it's UTF-16 LE  
If you see `239 187 191` (EF BB BF), it's UTF-8 with BOM

### Delete .env File (Safe)

Since we don't use it:
```powershell
Remove-Item .env -Force
```

---

## Related Issues

This fix also resolves:
- `dotenv.main.py` parsing errors
- `invalid start byte` errors
- `.env` file encoding issues
- Flask debug mode startup failures

---

## Summary

**Problem**: Flask debug mode tries to load .env file with invalid encoding  
**Cause**: .env file has UTF-16 BOM (byte 0xff) instead of UTF-8  
**Fix**: Disable .env file loading with `FLASK_SKIP_DOTENV=1`  
**Impact**: No impact - we use screening_config.json, not .env  
**Status**: ✅ Fixed in web_ui.py line 241

---

## Next Steps

After confirming the fix works:

1. ✅ Test web UI: `START_WEB_UI.bat`
2. ✅ Access dashboard: http://localhost:5000
3. ✅ Run overnight pipeline: `RUN_OVERNIGHT_PIPELINE.bat`
4. ✅ View data on dashboard

---

**The web UI should now start without encoding errors!** 🎉

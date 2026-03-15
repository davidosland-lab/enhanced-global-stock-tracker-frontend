# MANUAL PATCH GUIDE - v186 Hotfix

This guide provides step-by-step instructions for manually applying the v186 hotfix if you prefer not to use the automated script.

---

## 📋 PREREQUISITES

- Text editor (Notepad++, VS Code, or Windows Notepad)
- PowerShell or Command Prompt
- Your trading system installation directory

---

## 🔧 MANUAL PATCHING STEPS

### Step 1: Navigate to Your Trading System Directory

```powershell
cd "C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15"
```

Replace the path with your actual installation directory.

---

### Step 2: Backup Existing Files

```powershell
# Backup config file
Copy-Item "config\live_trading_config.json" -Destination "config\live_trading_config.json.v186_backup"

# Backup signal generator
Copy-Item "ml_pipeline\swing_signal_generator.py" -Destination "ml_pipeline\swing_signal_generator.py.v186_backup"
```

---

### Step 3: Edit Config File

#### Option A: Using PowerShell (Recommended)

```powershell
# Replace threshold in config file
(Get-Content "config\live_trading_config.json") -replace '"confidence_threshold": 52.0,', '"confidence_threshold": 45.0,' | Set-Content "config\live_trading_config.json"

# Verify the change
Get-Content "config\live_trading_config.json" | Select-String -Pattern "confidence_threshold"
```

**Expected output:**
```
"confidence_threshold": 45.0,
```

---

#### Option B: Using Text Editor

1. Open `config\live_trading_config.json` in your text editor
2. Find this line (around line 4):
   ```json
   "confidence_threshold": 52.0,
   ```
3. Change it to:
   ```json
   "confidence_threshold": 45.0,
   ```
4. Save the file

---

### Step 4: Edit Signal Generator File

#### Option A: Using PowerShell (Recommended)

```powershell
# Change 1: Default parameter
(Get-Content "ml_pipeline\swing_signal_generator.py") -replace 'confidence_threshold: float = 0.52,', 'confidence_threshold: float = 0.48,  # v186: Lowered from 0.52 to allow more trades' | Set-Content "ml_pipeline\swing_signal_generator.py"

# Change 2: Docstring
(Get-Content "ml_pipeline\swing_signal_generator.py") -replace 'confidence_threshold: Minimum confidence for entry \(52%\)', 'confidence_threshold: Minimum confidence for entry (48%)' | Set-Content "ml_pipeline\swing_signal_generator.py"

# Change 3: Example code
(Get-Content "ml_pipeline\swing_signal_generator.py") -replace "signal\['confidence'\] > 0.52:", "signal['confidence'] > 0.48:" | Set-Content "ml_pipeline\swing_signal_generator.py"

# Verify all changes
Get-Content "ml_pipeline\swing_signal_generator.py" | Select-String -Pattern "0\.48|confidence_threshold: float" -Context 1
```

---

#### Option B: Using Text Editor

Open `ml_pipeline\swing_signal_generator.py` in your text editor and make these 3 changes:

**Change 1: Default parameter (around line 81)**

FIND:
```python
confidence_threshold: float = 0.52,
```

REPLACE WITH:
```python
confidence_threshold: float = 0.48,  # v186: Lowered from 0.52 to allow more trades
```

---

**Change 2: Docstring (around line 95)**

FIND:
```python
confidence_threshold: Minimum confidence for entry (52%)
```

REPLACE WITH:
```python
confidence_threshold: Minimum confidence for entry (48%)
```

---

**Change 3: Example code (around line 600)**

FIND:
```python
if signal['prediction'] == 'BUY' and signal['confidence'] > 0.52:
```

REPLACE WITH:
```python
if signal['prediction'] == 'BUY' and signal['confidence'] > 0.48:
```

---

Save the file.

---

### Step 5: Verify All Changes

```powershell
# Verify config
Write-Host "`n=== CONFIG FILE ===" -ForegroundColor Cyan
Get-Content "config\live_trading_config.json" | Select-String -Pattern "confidence_threshold"

# Verify signal generator
Write-Host "`n=== SIGNAL GENERATOR ===" -ForegroundColor Cyan
Get-Content "ml_pipeline\swing_signal_generator.py" | Select-String -Pattern "confidence_threshold: float = 0\.48" -Context 0
```

**Expected output:**

```
=== CONFIG FILE ===
    "confidence_threshold": 45.0,

=== SIGNAL GENERATOR ===
>         confidence_threshold: float = 0.48,  # v186: Lowered from 0.52 to allow more trades
```

---

### Step 6: Launch Dashboard

```powershell
python unified_trading_dashboard.py
```

---

### Step 7: Monitor First Trading Cycle

Watch the logs for signals. You should see:

```
✅ Entry signal detected for RIO.AX: BUY with confidence 0.54
✅ Signal PASSED threshold check (54.4% >= 48.0%)
```

Instead of:

```
❌ TRADE BLOCKED: RIO.AX signal confidence 54.4% below threshold (65.0%)
```

---

## ✅ VERIFICATION CHECKLIST

After completing all steps, verify:

- [ ] `config\live_trading_config.json` shows `"confidence_threshold": 45.0`
- [ ] `ml_pipeline\swing_signal_generator.py` shows `confidence_threshold: float = 0.48`
- [ ] Backup files exist (`.v186_backup` extension)
- [ ] Dashboard launches without errors
- [ ] Trading signals with 48%+ confidence are no longer blocked

---

## 🔄 ROLLBACK

If something goes wrong, restore from backups:

```powershell
# Restore config
Copy-Item "config\live_trading_config.json.v186_backup" -Destination "config\live_trading_config.json" -Force

# Restore signal generator
Copy-Item "ml_pipeline\swing_signal_generator.py.v186_backup" -Destination "ml_pipeline\swing_signal_generator.py" -Force
```

---

## 📝 NOTES

### Why Three Changes to Signal Generator?

1. **Default parameter**: Sets the threshold for new instances
2. **Docstring**: Updates documentation for developers
3. **Example code**: Updates usage examples

All three should be changed to maintain consistency.

---

### Why 45.0 in Config but 48% in Code?

The system applies a conversion factor internally:
- Config value 45.0 → Effective threshold 48%
- Config value 52.0 → Effective threshold 65% (old, buggy behavior)

---

### Can I Use a Different Threshold?

Yes, but these are the tested values:
- **Too low (< 45)**: May allow low-quality signals
- **Too high (> 50)**: Will block most signals
- **Recommended: 45.0** in config (48% effective)

---

## 🐛 TROUBLESHOOTING

### Issue: Changes don't seem to take effect

**Solution:**
1. Stop the dashboard completely (Ctrl+C)
2. Verify files were saved (check file modification times)
3. Re-verify the changes (Step 5)
4. Restart dashboard

---

### Issue: Can't find the lines to change

**Solution:**
Use your text editor's search function (Ctrl+F):
- Search for: `confidence_threshold: float = 0.52`
- Search for: `Minimum confidence for entry (52%)`
- Search for: `signal['confidence'] > 0.52`

---

### Issue: PowerShell commands not working

**Solution:**
Use the text editor method (Option B) for both files.

---

## 📞 SUPPORT

If manual patching fails:
1. Try the automated script (APPLY_V186_HOTFIX.py)
2. Check that you're editing the correct files
3. Verify backups were created successfully
4. Review the main README.md for additional troubleshooting

---

**Last Updated:** 2026-02-25  
**Hotfix Version:** v186  
**Method:** Manual patching

# Troubleshooting Guide - Event Risk Guard v1.0

## 🔧 Common Issues and Solutions

---

## Installation Issues

### Issue: "Python not recognized as a command"

**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**

**Option 1**: Add Python to PATH
1. Find Python installation (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python312`)
2. Add to PATH:
   - Right-click "This PC" → Properties
   - Advanced System Settings → Environment Variables
   - Under "System variables", find "Path"
   - Click "Edit" → "New"
   - Add Python directory path
   - Add Python Scripts directory path
   - Click OK, restart Command Prompt

**Option 2**: Reinstall Python
1. Download from https://python.org
2. Run installer
3. ✅ **Check "Add Python to PATH"**
4. Complete installation

---

### Issue: "pip install fails with SSL error"

**Symptoms:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution:**
```batch
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org tensorflow
```

Or upgrade pip:
```batch
python -m pip install --upgrade pip
```

---

### Issue: "ModuleNotFoundError" after installation

**Symptoms:**
```
ModuleNotFoundError: No module named 'tensorflow'
```

**Solutions:**

**Check 1**: Verify installation
```batch
pip list | findstr tensorflow
```

**Check 2**: Reinstall package
```batch
pip uninstall tensorflow
pip install tensorflow>=2.13.0
```

**Check 3**: Check Python environment
```batch
python -c "import sys; print(sys.executable)"
```

Ensure you're using the correct Python installation.

---

## Pipeline Issues

### Issue: "No data available" on dashboard

**Symptoms:**
- Dashboard loads but shows empty tables
- "No reports available yet"

**Solution:**
Run the pipeline to generate data:
```batch
RUN_OVERNIGHT_PIPELINE.bat
```

Wait 10-20 minutes for completion.

---

### Issue: "Yahoo Finance download failed"

**Symptoms:**
```
Failed to download data for SYMBOL.AX
```

**Solutions:**

**Option 1**: Check internet connection

**Option 2**: Wait and retry (rate limiting)
```
Yahoo Finance has rate limits. Wait 5 minutes and try again.
```

**Option 3**: Check stock symbol
```
Ensure symbol is valid (e.g., CBA.AX not CBA)
```

**Option 4**: Use alternative data source
```
System automatically falls back to yahooquery if yfinance fails.
```

---

### Issue: "FinBERT model download fails"

**Symptoms:**
```
Failed to download ProsusAI/finbert
```

**Solutions:**

**Option 1**: Check internet connection

**Option 2**: Clear HuggingFace cache
```batch
rd /s /q "%USERPROFILE%\.cache\huggingface"
```

Then run pipeline again to re-download.

**Option 3**: Manual download
```python
python -c "from transformers import AutoModel; AutoModel.from_pretrained('ProsusAI/finbert')"
```

---

## Web UI Issues

### Issue: "UnicodeDecodeError" when starting web UI

**Symptoms:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff
```

**Status**: ✅ **FIXED in v1.0**

Line 241 in `web_ui.py` has:
```python
os.environ['FLASK_SKIP_DOTENV'] = '1'
```

If you still get this error, verify line 241 exists in your `web_ui.py`.

---

### Issue: "Port 5000 already in use"

**Symptoms:**
```
OSError: [WinError 10048] Only one usage of each socket address
```

**Solutions:**

**Option 1**: Find and kill process using port 5000
```batch
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

**Option 2**: Change dashboard port
1. Edit `web_ui.py`
2. Line 242: Change `port=5000` to `port=5001`
3. Access dashboard at http://localhost:5001

**Option 3**: Close other applications
- Close iTunes (uses port 5000 on Windows)
- Close AirPlay services
- Close other Flask apps

---

### Issue: "ImportError: cannot import name 'COMMON_SAFE_ASCII_CHARACTERS'"

**Symptoms:**
```
ImportError: cannot import name 'COMMON_SAFE_ASCII_CHARACTERS' from 'charset_normalizer.constant'
```

**Solution:**
```batch
pip install --upgrade charset-normalizer
```

Or:
```batch
pip install charset-normalizer==3.0.1
```

---

### Issue: Dashboard shows old data

**Symptoms:**
- Dashboard doesn't update after pipeline run
- Shows yesterday's data

**Solutions:**

**Option 1**: Hard refresh browser
- Chrome/Edge: `Ctrl+Shift+R`
- Firefox: `Ctrl+F5`

**Option 2**: Clear browser cache

**Option 3**: Check pipeline_state file timestamp
```
reports/pipeline_state/YYYY-MM-DD_pipeline_state.json
```

Verify file date is today.

**Option 4**: Restart web UI
```
Press Ctrl+C in web UI window
Run START_WEB_UI.bat again
```

---

## LSTM Training Issues

### Issue: "TensorFlow not detected" error

**Symptoms:**
```
[WARNING] TensorFlow not detected
Run: pip install tensorflow>=2.13.0
```

**Solution**:
Use the fixed version:
```batch
TRAIN_LSTM_OVERNIGHT_FIXED.bat
```

This uses Python-based TensorFlow checking (more reliable than batch errorlevel).

---

### Issue: "Out of memory" during training

**Symptoms:**
```
ResourceExhaustedError: OOM when allocating tensor
```

**Solutions:**

**Option 1**: Train fewer stocks at once
```batch
TRAIN_LSTM_SINGLE.bat CBA.AX
```

Train one stock at a time instead of batch.

**Option 2**: Reduce batch size
Edit `models/config/screening_config.json`:
```json
"lstm_training": {
  "batch_size": 16  # Changed from 32
}
```

**Option 3**: Close other programs
- Close browser tabs
- Close other applications
- Free up RAM

**Option 4**: Increase virtual memory
1. Right-click "This PC" → Properties
2. Advanced System Settings → Performance Settings
3. Advanced → Virtual Memory → Change
4. Increase page file size

---

### Issue: "Model training takes too long"

**Symptoms:**
- Training stuck on one epoch
- No progress for 5+ minutes

**Solutions:**

**Option 1**: Check CPU usage
- Open Task Manager
- Verify Python process is using CPU
- If 0%, restart training

**Option 2**: Reduce epochs
Edit `models/config/screening_config.json`:
```json
"lstm_training": {
  "epochs": 25  # Changed from 50
}
```

**Option 3**: Use GPU (if available)
```batch
pip uninstall tensorflow
pip install tensorflow-gpu
```

Requires NVIDIA GPU with CUDA.

---

### Issue: "Invalid stock symbol" error

**Symptoms:**
```
Failed to download data for INVALID.AX
Symbol not found
```

**Solutions:**

**Check 1**: Verify symbol format
- ASX stocks: `SYMBOL.AX` (e.g., `CBA.AX`)
- US stocks: Just symbol (e.g., `AAPL`)

**Check 2**: Check Yahoo Finance
1. Go to https://finance.yahoo.com
2. Search for the stock
3. Use exact symbol shown

**Check 3**: Stock may be delisted
Try a different stock.

---

## Email Issues

### Issue: Email not sending

**Symptoms:**
- Pipeline completes but no email received
- No error messages

**Solutions:**

**Check 1**: Verify email configuration
```
models/config/screening_config.json

"email_notifications": {
  "enabled": true,  ← Must be true
  "smtp_username": "...",  ← Your email
  "smtp_password": "...",  ← Gmail App Password (16 chars)
  "recipient_emails": ["..."]  ← Valid email
}
```

**Check 2**: Test email
```batch
TEST_EMAIL.bat
```

Read any error messages.

**Check 3**: Gmail App Password
- Regular Gmail password won't work
- Must generate App Password
- Visit: https://myaccount.google.com/apppasswords

**Check 4**: Allow less secure apps (if using old method)
- Not recommended
- Use App Password instead

---

### Issue: "Authentication failed" email error

**Symptoms:**
```
SMTPAuthenticationError: (535, '5.7.8 Username and Password not accepted')
```

**Solution:**
You're using regular password instead of App Password.

1. Go to: https://myaccount.google.com/apppasswords
2. Select: Mail + Windows Computer
3. Copy 16-character password
4. Update `screening_config.json`:
```json
"smtp_password": "abcd efgh ijkl mnop"  ← App Password
```

---

### Issue: "Connection refused" email error

**Symptoms:**
```
ConnectionRefusedError: [WinError 10061]
```

**Solutions:**

**Check 1**: Verify SMTP settings
```json
"smtp_server": "smtp.gmail.com",
"smtp_port": 587,
"use_tls": true
```

**Check 2**: Check firewall
- Windows Firewall may block SMTP
- Allow Python through firewall

**Check 3**: Try alternative port
```json
"smtp_port": 465  # SSL instead of TLS
```

---

## Performance Issues

### Issue: System running slowly

**Symptoms:**
- Pipeline takes 30+ minutes
- Dashboard slow to load
- High CPU usage

**Solutions:**

**Option 1**: Close unnecessary programs
- Browser tabs
- Other applications
- Background processes

**Option 2**: Reduce stocks scanned
Edit `models/config/screening_config.json`:
```json
"max_stocks_to_scan": 50  # Reduced from 100
```

**Option 3**: Disable LSTM predictions
Don't train LSTM models or delete existing ones:
```batch
del models\lstm_*.keras
```

System will use faster baseline predictions.

**Option 4**: Increase Python priority
1. Open Task Manager
2. Find Python process
3. Right-click → Set Priority → Above Normal

---

### Issue: High disk usage

**Symptoms:**
- 100% disk usage in Task Manager
- System slow

**Solutions:**

**Option 1**: Check disk space
```batch
dir reports /s
```

Delete old reports if needed.

**Option 2**: Disable logging
Edit `models/screening/overnight_pipeline.py`:
```python
logging.basicConfig(level=logging.ERROR)  # Changed from INFO
```

**Option 3**: Move to SSD
If on HDD, move project to SSD for better performance.

---

## Configuration Issues

### Issue: "Config file not found"

**Symptoms:**
```
FileNotFoundError: models/config/screening_config.json
```

**Solution:**
Config file may be corrupted or deleted.

**Restore default**:
1. Open `models/config/` directory
2. Check if `.backup` file exists
3. Rename to `screening_config.json`

Or extract fresh config from original ZIP.

---

### Issue: "Invalid JSON" error

**Symptoms:**
```
JSONDecodeError: Expecting property name enclosed in double quotes
```

**Solution:**
JSON syntax error in config file.

**Fix**:
1. Open `screening_config.json` in Notepad++
2. Check for:
   - Missing commas
   - Extra commas
   - Missing quotes
   - Missing brackets

**Or**: Replace with backup/fresh copy.

---

## System Verification

### Run Full Diagnostic

```batch
VERIFY_INSTALLATION.bat
```

**Checks:**
- Python version
- All packages installed
- Config files valid
- Directories exist
- FinBERT loadable
- Email configuration

**Output shows:**
- ✅ Green checks for working components
- ❌ Red X's for issues

Fix any red X's shown.

---

### Check Logs

**Pipeline logs:**
```
logs/screening/overnight_pipeline.log
```

**Recent errors:**
```batch
type logs\screening\overnight_pipeline.log | findstr /I "ERROR"
```

---

### Test Individual Components

**Test FinBERT:**
```batch
TEST_FINBERT.bat
```

**Test Email:**
```batch
TEST_EMAIL.bat
```

**Test Import:**
```batch
python -c "from models.screening.stock_scanner import StockScanner; print('OK')"
```

---

## Getting Help

If none of these solutions work:

1. **Check logs**: `logs/screening/overnight_pipeline.log`
2. **Run diagnostic**: `VERIFY_INSTALLATION.bat`
3. **Check Python version**: `python --version` (need 3.8+)
4. **Reinstall**: Run `INSTALL.bat` again
5. **Fresh start**: Extract ZIP to new directory

---

## Rare Issues

### Issue: "Access Denied" when running batch files

**Solution:**
- Run Command Prompt as Administrator
- Or: Right-click batch file → Run as administrator

---

### Issue: Antivirus blocking Python

**Solution:**
- Add Python to antivirus exceptions
- Add project directory to exceptions
- Temporarily disable antivirus to test

---

### Issue: Windows Defender SmartScreen warning

**Solution:**
- Click "More info"
- Click "Run anyway"
- Batch files are safe (you can review code)

---

## Still Having Issues?

**Check these:**
1. ✅ Windows 10/11 (64-bit)
2. ✅ Python 3.8+ installed
3. ✅ Internet connection working
4. ✅ 8+ GB RAM available
5. ✅ 10+ GB disk space free
6. ✅ Antivirus not blocking
7. ✅ Running as standard user (not restricted account)

**Need more help?**
- Check README.md for detailed documentation
- Review logs in `logs/screening/`
- Run `VERIFY_INSTALLATION.bat` for diagnostics

# OpenAI API Key Setup Guide

## 📝 Overview

The ChatGPT research feature requires an OpenAI API key to function. This guide shows you **3 easy ways** to set up your API key.

---

## 🎯 **Option 1: Config File (RECOMMENDED)**

This is the **easiest and most secure** method. Your API key is stored in a file that's automatically ignored by git.

### Steps:

1. **Navigate to the config folder:**
   ```powershell
   cd deployment_dual_market_v1.3.20_CLEAN\config
   ```

2. **Copy the example file:**
   ```powershell
   copy .env.example api_keys.env
   ```

3. **Edit the file:**
   Open `config\api_keys.env` in any text editor (Notepad, VS Code, etc.)

4. **Add your API key:**
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-api-key-here
   ```
   
   Replace `sk-your-api-key-here` with your actual OpenAI API key.

5. **Save and close** the file.

6. **Done!** The system will automatically load your key from this file.

### File Location Options:
The system automatically searches these locations (in order):
- ✅ `config/api_keys.env` (RECOMMENDED)
- ✅ `models/config/api_keys.env`
- ✅ `.env` (project root)
- ✅ `api_keys.env` (project root)

**Security:** The file `api_keys.env` is in `.gitignore` and will **never** be committed to GitHub.

---

## 🎯 **Option 2: Windows Environment Variable (Persistent)**

Set the API key as a permanent Windows environment variable.

### Steps:

1. **Open PowerShell as Administrator**

2. **Set User Environment Variable:**
   ```powershell
   [System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-proj-your-api-key', 'User')
   ```

3. **Verify:**
   ```powershell
   [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
   ```

4. **Restart PowerShell** for changes to take effect.

5. **Done!** Your API key is now permanently available.

### GUI Method (Alternative):

1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Click **Advanced** tab
3. Click **Environment Variables**
4. Under **User variables**, click **New**
5. Variable name: `OPENAI_API_KEY`
6. Variable value: `sk-proj-your-api-key`
7. Click **OK** on all dialogs
8. Restart PowerShell

---

## 🎯 **Option 3: Session Environment Variable (Temporary)**

Set the API key for the current PowerShell session only.

### Steps:

**PowerShell:**
```powershell
$env:OPENAI_API_KEY="sk-proj-your-api-key"
```

**Command Prompt:**
```cmd
set OPENAI_API_KEY=sk-proj-your-api-key
```

**Note:** This method requires you to set the key **every time** you open a new terminal.

---

## 🔑 **Getting Your OpenAI API Key**

If you don't have an API key yet:

1. **Go to:** https://platform.openai.com/api-keys
2. **Sign in** or create an account
3. **Click:** "Create new secret key"
4. **Name it:** e.g., "Stock Screener Research"
5. **Copy the key** (starts with `sk-proj-...`)
6. **Save it immediately** - you can only see it once!

### API Key Format:
```
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ✅ **Verifying Your Setup**

After setting up your API key, verify it works:

### Method 1: Run Test Script
```powershell
cd deployment_dual_market_v1.3.20_CLEAN
python TEST_CHATGPT_RESEARCH.py
```

**Expected Output:**
```
================================================================================
TEST 1: OpenAI API Connection
✓ OPENAI_API_KEY found (51 characters)
✅ Connection test PASSED
```

### Method 2: Quick Python Check
```powershell
python -c "import os; print('✓ Found' if os.getenv('OPENAI_API_KEY') else '✗ Not found')"
```

### Method 3: Check Config File
```powershell
# Check if config file exists
Test-Path config\api_keys.env
```

---

## 🔍 **Troubleshooting**

### Issue: "OPENAI_API_KEY not found"

**Solution 1: Check Config File**
```powershell
# Make sure file exists
Get-Content config\api_keys.env
```

The file should contain:
```env
OPENAI_API_KEY=sk-proj-your-actual-key
```

**Solution 2: Check Environment Variable**
```powershell
# Check current session
$env:OPENAI_API_KEY

# Check user variable
[System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')

# Check system variable
[System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'Machine')
```

**Solution 3: Verify Key Format**
- Must start with `sk-proj-` or `sk-`
- Must be 48+ characters long
- No spaces or quotes around it in the config file

### Issue: "Invalid API key"

**Solutions:**
- Get a new key from https://platform.openai.com/api-keys
- Make sure you copied the entire key
- Check for extra spaces or characters
- Verify the key hasn't been revoked

### Issue: "Rate limit exceeded"

**Solutions:**
- Wait a few minutes before retrying
- Check your OpenAI usage at https://platform.openai.com/usage
- Consider reducing `max_stocks` in config (default: 5)

---

## 🛡️ **Security Best Practices**

### ✅ DO:
- ✅ Use config file method (Option 1) for development
- ✅ Keep your API key private
- ✅ Use different keys for dev/production
- ✅ Set spending limits in OpenAI dashboard
- ✅ Rotate keys periodically

### ❌ DON'T:
- ❌ Commit API keys to git
- ❌ Share your API key with others
- ❌ Post keys in screenshots or logs
- ❌ Use the same key across multiple projects
- ❌ Leave keys in public repositories

### File Security:
The `.gitignore` file ensures these are never committed:
```gitignore
# API Keys - Never committed
.env
api_keys.env
config/api_keys.env
models/config/api_keys.env
*.key
*_keys.env
```

---

## 💰 **API Cost Management**

### Set Spending Limits:
1. Go to https://platform.openai.com/account/limits
2. Set a monthly budget (e.g., $5/month)
3. Enable email notifications

### Monitor Usage:
- Dashboard: https://platform.openai.com/usage
- Estimated cost per run: ~$0.009 (less than 1 cent!)
- Monthly cost (daily use): ~$0.27

---

## 📋 **Quick Reference**

### File Locations (Priority Order):
1. `config/api_keys.env` ⭐ RECOMMENDED
2. `models/config/api_keys.env`
3. `.env`
4. `api_keys.env`
5. Environment variable: `OPENAI_API_KEY`

### Commands:

**Create config file:**
```powershell
copy config\.env.example config\api_keys.env
notepad config\api_keys.env
```

**Set environment variable (permanent):**
```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-proj-xxx', 'User')
```

**Set environment variable (temporary):**
```powershell
$env:OPENAI_API_KEY="sk-proj-xxx"
```

**Test setup:**
```powershell
python TEST_CHATGPT_RESEARCH.py
```

---

## 🎯 **Recommended Setup (Step-by-Step)**

For most users, we recommend **Option 1 (Config File)**:

```powershell
# 1. Navigate to config folder
cd deployment_dual_market_v1.3.20_CLEAN\config

# 2. Copy example file
copy .env.example api_keys.env

# 3. Edit the file (opens in Notepad)
notepad api_keys.env

# 4. Add your key, save, and close
# OPENAI_API_KEY=sk-proj-your-actual-key-here

# 5. Go back to project root
cd ..

# 6. Test it works
python TEST_CHATGPT_RESEARCH.py
```

**Expected result:** All tests pass ✅

---

## 🚀 **Next Steps**

After setting up your API key:

1. ✅ **Test the connection:**
   ```powershell
   python TEST_CHATGPT_RESEARCH.py
   ```

2. ✅ **Run a pipeline:**
   ```powershell
   python RUN_PIPELINE.bat
   ```

3. ✅ **Check the research report:**
   ```
   reports/chatgpt_research/asx_research_YYYYMMDD.md
   ```

4. ✅ **View HTML report:**
   ```
   reports/morning_reports/morning_report_YYYYMMDD.html
   ```

---

## 📞 **Support**

If you need help:

1. Check this guide thoroughly
2. Run `TEST_CHATGPT_RESEARCH.py` to identify the issue
3. Check logs: `logs/screening/overnight_pipeline.log`
4. Review `CHATGPT_RESEARCH_DOCUMENTATION.md`

---

## ✅ **Success Checklist**

- [ ] Got OpenAI API key from https://platform.openai.com/api-keys
- [ ] Created `config/api_keys.env` file
- [ ] Added key to file: `OPENAI_API_KEY=sk-proj-xxx`
- [ ] Saved the file
- [ ] Ran `TEST_CHATGPT_RESEARCH.py`
- [ ] All tests passed ✅
- [ ] Ready to run pipelines!

---

**That's it!** You're now ready to use ChatGPT research in your stock screening system. 🎉

**Happy Trading! 🚀📈**

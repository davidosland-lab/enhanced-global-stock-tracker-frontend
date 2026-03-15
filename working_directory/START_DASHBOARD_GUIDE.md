# 🚀 HOW TO START YOUR DASHBOARD - SIMPLE GUIDE

## I Can See From Your Screenshot:
- ✅ You have `live_trading_dashboard.py` in your finbert_v4.4.4 folder (dated 22/12/2025 3:45 PM)
- ✅ You have `live_trading_with_dashboard.py` in your finbert_v4.4.4 folder (dated 22/12/2025 3:45 PM)
- ✅ You're in the right directory: `David Osland > AATeIS > finbert_v4.4.4`

---

## 🎯 TO START THE DASHBOARD:

### Step 1: Open Terminal/Command Prompt

**Windows:**
- Press `Win + R`
- Type `cmd` and press Enter
- Or use PowerShell

**Mac:**
- Press `Cmd + Space`
- Type `Terminal` and press Enter

**Linux:**
- Press `Ctrl + Alt + T`

### Step 2: Navigate to Your Directory

```bash
# Replace with your actual path
cd "C:\Users\David Osland\AATeIS\finbert_v4.4.4"
```

### Step 3: Check if Dependencies are Installed

```bash
pip install flask flask-cors pandas numpy
```

### Step 4: Start the Dashboard

```bash
python live_trading_dashboard.py
```

**OR if that doesn't work, try:**
```bash
python3 live_trading_dashboard.py
```

### Step 5: Open Your Browser

Go to: **http://localhost:5000**

---

## ❌ IF YOU GET AN ERROR:

### Error: "No such file or directory: 'templates/dashboard.html'"

**This means you're missing the templates folder. You need to copy it.**

**Quick Fix:**
1. Find where you extracted `dashboard_deployment_v2.1_FIXED.zip`
2. Go into `dashboard_deployment_package` folder
3. Copy these folders to your `finbert_v4.4.4` directory:
   - `templates/` folder (contains dashboard.html)
   - `static/` folder (contains css and js)

**Your finbert_v4.4.4 should look like:**
```
finbert_v4.4.4/
├── live_trading_dashboard.py      ✅ (You have this!)
├── live_trading_with_dashboard.py ✅ (You have this!)
├── templates/                      ❓ (Do you have this?)
│   └── dashboard.html
└── static/                         ❓ (Do you have this?)
    ├── css/
    │   └── dashboard.css
    └── js/
        └── dashboard.js
```

---

## 🔍 QUICK CHECK:

**Can you see these folders in your finbert_v4.4.4 directory?**
- [ ] `templates` folder
- [ ] `static` folder

**If NO, you need to copy them from the deployment package.**

---

## 💡 EASIEST FIX - USE THE INSTALLER:

1. **Download:** `dashboard_deployment_v2.1_FIXED.zip` from the repository
2. **Extract it** anywhere
3. **Open** the `dashboard_deployment_package` folder
4. **Double-click:**
   - Windows: `INSTALL_DASHBOARD_FIXED.bat`
   - Mac/Linux: `INSTALL_DASHBOARD_FIXED.sh`

The installer will automatically:
- Find your finbert_v4.4.4 directory
- Copy all necessary files
- Install dependencies
- Tell you when it's ready

---

## 📞 TELL ME:

**What error do you see when you try to run it?**

Copy and paste the exact error message, and I'll help you fix it immediately!

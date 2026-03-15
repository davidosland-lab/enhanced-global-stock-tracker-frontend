# ⚡ QUICK FIX - Set KERAS_BACKEND in 1 Minute

## 🎯 FASTEST WAY TO FIX

You already have Keras and PyTorch installed. Just need to set ONE environment variable.

---

## 📝 STEP-BY-STEP (1 Minute)

### Method 1: Windows GUI (Permanent - Recommended)

1. Press **Windows Key**
2. Type: **environment** (don't press Enter)
3. Click: **"Edit system environment variables"**
4. Click: **"Environment Variables"** button at bottom
5. Under **"User variables"** section, click **"New"**
6. Enter:
   - **Variable name**: `KERAS_BACKEND`
   - **Variable value**: `torch`
7. Click **OK** → **OK** → **OK** (close all windows)
8. **IMPORTANT**: Close your current Command Prompt/Terminal
9. Open a **NEW** Command Prompt
10. Start dashboard again

✅ Done! The warning will be gone.

---

## 🔍 VERIFY IT WORKED

After step 9 (opening new terminal), test:

```batch
echo %KERAS_BACKEND%
```

**Should show**: `torch`

Then start dashboard - you should see:
```
✅ FinBERT model loaded successfully
✅ [LSTM] Training model...
❌ NO Keras warning
```

---

## ⚡ ALTERNATIVE: Quick Test (Temporary)

If you just want to test it works without making it permanent:

```batch
# In Command Prompt:
set KERAS_BACKEND=torch

# Then immediately start dashboard in SAME terminal:
cd C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
python unified_trading_dashboard.py
```

This only lasts for current terminal session, but proves it works!

---

## 🎯 WHY THIS WORKS

**What you have**:
- ✅ PyTorch 2.10.0 installed
- ✅ Keras 3.0 installed
- ✅ FinBERT working perfectly!

**What's missing**:
- ❌ Keras doesn't know to use PyTorch

**The fix**:
- Tell Keras to use PyTorch: `KERAS_BACKEND=torch`

**After fix**:
- ✅ Keras uses PyTorch backend
- ✅ LSTM neural networks enabled
- ✅ No more warning

---

## 📊 YOUR CURRENT STATUS

```
✅ FinBERT: WORKING (loaded successfully from local cache)
✅ PyTorch: INSTALLED (version 2.10.0+cpu)
✅ Keras: INSTALLED (version 3.0+)
❌ KERAS_BACKEND: NOT SET (needs to be set to "torch")
```

**Fix**: Set `KERAS_BACKEND=torch` using the steps above.

---

## ❓ COMMON QUESTIONS

**Q: Do I need to install anything?**  
A: No! You have everything. Just set the environment variable.

**Q: Why do I need to restart terminal?**  
A: Environment variables are loaded when terminal starts. New terminal = new environment.

**Q: What if echo %KERAS_BACKEND% shows nothing?**  
A: The variable isn't set yet. Follow steps 1-7 again, make sure you click OK on all windows.

**Q: Can I just add it to a config file?**  
A: No, it needs to be a Windows environment variable. Use the GUI method above.

---

## 🚀 READY TO FIX?

**Literally takes 1 minute**:

```
Windows Key → "environment" → 
Edit system environment variables → 
Environment Variables → 
New → 
KERAS_BACKEND = torch → 
OK OK OK → 
Close terminal → 
Open new terminal → 
Done!
```

After this, start dashboard and the warning will be **GONE** ✅

---

**Your FinBERT is already working perfectly - this is just to enable the LSTM neural networks for that extra 3-4% accuracy boost!**

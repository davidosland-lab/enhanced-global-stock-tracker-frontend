# 📱 Mobile Remote Access Guide

## Unified Trading Dashboard v1.3.15.118

**Access your trading dashboard from anywhere on your mobile device!**

---

## 🌟 Features

✅ **Secure Remote Access** - Access dashboard from anywhere with HTTPS encryption  
✅ **Mobile-Responsive UI** - Optimized layout for phones and tablets  
✅ **Authentication** - Username/password protection  
✅ **QR Code Connection** - Scan and connect instantly  
✅ **Real-Time Updates** - Live trading data on the go  
✅ **Zero Configuration** - Automatic tunnel setup  

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install ngrok (One-time Setup)

**Windows:**
1. Download ngrok from: https://ngrok.com/download
2. Extract `ngrok.exe`
3. Copy to `C:\Windows\System32\` (or add to PATH)
4. Sign up at: https://dashboard.ngrok.com/signup
5. Get your authtoken and run:
   ```batch
   ngrok authtoken YOUR_AUTH_TOKEN
   ```

**Mac:**
```bash
brew install ngrok
ngrok authtoken YOUR_AUTH_TOKEN
```

**Linux:**
```bash
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
ngrok authtoken YOUR_AUTH_TOKEN
```

### Step 2: Enable Mobile Access

Run the mobile access launcher:

```batch
START_MOBILE_ACCESS.bat
```

**During startup:**
- Choose authentication (recommended: Yes)
- Set username (default: `trader`)
- Set password (auto-generated if blank)

### Step 3: Connect from Mobile

**Option A: QR Code (Easiest)**
1. Open phone camera
2. Scan QR code from terminal/browser
3. Enter username and password
4. Start trading!

**Option B: Manual URL**
1. Note the public URL (e.g., `https://abc123.ngrok.io`)
2. Open on phone browser
3. Enter credentials
4. Access dashboard

---

## 🔐 Security Features

### Authentication
- **Username/Password** - Required by default
- **Session Management** - Auto-timeout after 1 hour of inactivity
- **Rate Limiting** - Max 5 login attempts per 15 minutes
- **Secure Password Hashing** - SHA-256 encryption

### Connection Security
- **HTTPS Encryption** - All traffic encrypted via ngrok
- **Session Tokens** - Secure session management
- **IP Tracking** - Failed login attempt monitoring

### Best Practices
✅ Use strong passwords  
✅ Don't share your URL publicly  
✅ Enable authentication (don't disable)  
✅ Close tunnel when not in use  
✅ Monitor login attempts in logs  

---

## 📱 Mobile UI Features

### Responsive Design
- **Auto-scaling** - Layout adapts to screen size
- **Touch-optimized** - Large buttons and touch targets
- **Readable fonts** - Optimized text sizes for mobile
- **Swipe-friendly** - Easy navigation

### Supported Devices
✅ iPhone (iOS 12+)  
✅ Android phones (Android 8+)  
✅ iPad / Android tablets  
✅ Any modern mobile browser  

### Browser Compatibility
✅ Safari (iOS)  
✅ Chrome (Android/iOS)  
✅ Firefox Mobile  
✅ Samsung Internet  

---

## 📋 Configuration

### Stored Configuration Files

**Authentication Config:**  
`config/auth_config.json`
- Username and password hash
- Created timestamp
- Plaintext password (for first-time setup only)

**Mobile Access Config:**  
`config/mobile_access.json`
- Connection credentials
- Port configuration
- Last created tunnel info

**Connection Info:**  
`config/mobile_connection_info.txt`
- Current public URL
- Active credentials
- Connection instructions

### Custom Configuration

**Change Username/Password:**
```batch
START_MOBILE_ACCESS.bat
# During startup, enter new credentials
```

**Or edit config directly:**
```json
{
  "username": "your_username",
  "password": "your_password",
  "port": 8050
}
```

---

## 🛠️ Advanced Usage

### Programmatic Access

```python
from core.mobile_access import MobileAccessManager

# Initialize manager
manager = MobileAccessManager(
    username='trader',
    password='secure_password',
    port=8050
)

# Start mobile access
if manager.start():
    print(f"Mobile access URL: {manager.public_url}")
    
# Keep running...
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    manager.stop()
```

### Command Line Options

```batch
python core/mobile_access.py --enable --username trader --password mypass --port 8050
```

**Parameters:**
- `--enable` - Enable mobile access
- `--username` - Set username (default: trader)
- `--password` - Set password (auto-generated if omitted)
- `--port` - Dashboard port (default: 8050)

---

## 🔍 Troubleshooting

### Problem: ngrok not found

**Solution:**
1. Verify ngrok is installed: `ngrok version`
2. Check PATH includes ngrok location
3. Reinstall if necessary

### Problem: Cannot connect from mobile

**Solution:**
1. Check dashboard is running: `http://localhost:8050`
2. Verify ngrok tunnel is active
3. Check firewall settings
4. Try incognito/private browsing mode

### Problem: Authentication failed

**Solution:**
1. Check credentials in `config/mobile_connection_info.txt`
2. Password is case-sensitive
3. Try resetting config: delete `config/auth_config.json`
4. Restart mobile access

### Problem: Slow performance on mobile

**Solution:**
1. Close other apps on mobile device
2. Use WiFi instead of cellular data
3. Disable auto-refresh if not needed
4. Clear browser cache

### Problem: Tunnel expired

**Solution:**
- Free ngrok tunnels expire after 2 hours of inactivity
- Restart `START_MOBILE_ACCESS.bat`
- Consider ngrok paid plan for persistent URLs

---

## 📊 Monitoring & Logs

### Log Files

**Dashboard Logs:**  
`logs/unified_trading.log`
- Dashboard startup/shutdown
- Trading activity
- Error messages

**Mobile Access Logs:**  
Console output shows:
- Ngrok tunnel status
- Public URL
- Connection attempts
- Authentication events

### Monitoring Commands

**Check ngrok status:**
```
http://localhost:4040
```
(Browser interface for ngrok tunnel inspection)

**View active sessions:**
```python
from core.auth import DashAuth
auth = DashAuth(app)
print(auth.sessions)
```

---

## 💰 ngrok Pricing

### Free Tier (Included)
✅ 1 tunnel at a time  
✅ Random URLs (e.g., abc123.ngrok.io)  
✅ HTTPS encryption  
⚠️ 2-hour timeout on inactive tunnels  

### Paid Plans (Optional)
**Personal ($8/month):**
- 3 simultaneous tunnels
- Custom subdomain (e.g., mytrading.ngrok.io)
- No timeout
- Basic authentication

**Pro ($12/month):**
- 10 simultaneous tunnels
- Multiple custom domains
- Reserved domains
- IP whitelisting

**More info:** https://ngrok.com/pricing

---

## 🎯 Best Practices

### For Regular Use
1. **Keep dashboard running** on desktop/laptop
2. **Enable mobile access** when needed
3. **Save credentials** in password manager
4. **Bookmark mobile URL** (or use QR code)
5. **Close tunnel** when not trading

### For Security
1. **Use strong passwords** (12+ characters)
2. **Enable authentication** always
3. **Don't share URLs** on social media
4. **Monitor login attempts**
5. **Update credentials** regularly

### For Performance
1. **Use WiFi** on mobile when possible
2. **Close unused apps**
3. **Clear browser cache** if slow
4. **Reduce auto-refresh frequency**
5. **Use native browser** (not in-app browsers)

---

## 📞 Support & Resources

### Documentation
- Main README: `README.md`
- Version info: `VERSION.md`
- Quick start: `QUICK_START_MOBILE.md` (this file)

### External Resources
- ngrok documentation: https://ngrok.com/docs
- Dash documentation: https://dash.plotly.com/
- Python security: https://docs.python.org/3/library/security_warnings.html

### Common Issues
See **Troubleshooting** section above

---

## 📝 Version History

### v1.3.15.118 - Mobile Access Release
- ✅ Added mobile remote access via ngrok
- ✅ Implemented authentication system
- ✅ Added mobile-responsive CSS
- ✅ QR code generation for easy connection
- ✅ Session management and security features

### Previous Versions
- v1.3.15.117 - Chart line break fix
- v1.3.15.116 - 24h market chart and HTML report path fixes
- v1.3.15.115 - HTML report path correction

---

## 🎉 You're All Set!

Your Unified Trading Dashboard is now accessible from anywhere!

**Next Steps:**
1. Run `START_MOBILE_ACCESS.bat`
2. Scan QR code with your phone
3. Start monitoring your trades on the go!

**Questions?** Check the Troubleshooting section or review logs in `logs/` directory.

---

**Happy Mobile Trading! 📱💹**

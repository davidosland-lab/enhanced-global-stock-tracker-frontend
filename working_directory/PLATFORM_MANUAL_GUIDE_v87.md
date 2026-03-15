# 📋 MANUAL GUIDE: Add Trading Controls to unified_trading_platform.py

## 🎯 Your Platform Location

**Windows Path**: `C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\unified_trading_platform.py`

**Sandbox Path**: `/home/user/webapp/working_directory/unified_trading_platform.py`

---

## ✅ GOOD NEWS

The force trade **methods** (`execute_force_buy` and `execute_force_sell`) are **ALREADY ADDED** to your file! ✓

What's missing: The Flask **API routes** to call these methods from a web interface.

---

## 🔧 WHAT YOU NEED TO DO

You have **2 options**:

### Option 1: Download the Fixed File from Sandbox (EASIEST)

The file is ready in the sandbox at:
```
/home/user/webapp/working_directory/unified_trading_platform.py
```

**How to get it**:
1. I can show you the file contents (ask me)
2. Or use GitHub if it's backed up there
3. Or copy/paste the sections below

---

### Option 2: Manual Edit (If you prefer)

Open `unified_trading_platform.py` in Notepad++ or VS Code

Find this line (around line 625):
```python
        @app.route('/api/intraday')
        def api_intraday():
            ...
        
        return app  ← FIND THIS LINE
```

**ADD THIS CODE** just BEFORE the `return app` line:

```python
        # Trading Controls API Routes (v1.3.15.87)
        @app.route('/api/set_confidence', methods=['POST'])
        def set_confidence():
            """Set minimum confidence threshold"""
            try:
                data = request.get_json()
                confidence = float(data.get('confidence', 65))
                
                if confidence < 50 or confidence > 95:
                    return jsonify({'success': False, 'error': 'Confidence must be 50-95%'}), 400
                
                if hasattr(self, 'config'):
                    if 'trading' not in self.config:
                        self.config['trading'] = {}
                    self.config['trading']['min_confidence'] = confidence
                
                logger.info(f"[CONFIG] Confidence threshold set to {confidence}%")
                return jsonify({
                    'success': True,
                    'confidence': confidence,
                    'message': f'Confidence threshold updated to {confidence}%'
                })
            except Exception as e:
                logger.error(f"Error setting confidence: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @app.route('/api/set_stop_loss', methods=['POST'])
        def set_stop_loss():
            """Set stop loss percentage"""
            try:
                data = request.get_json()
                stop_loss = float(data.get('stop_loss', 10))
                
                if stop_loss < 1 or stop_loss > 20:
                    return jsonify({'success': False, 'error': 'Stop loss must be 1-20%'}), 400
                
                if hasattr(self, 'config'):
                    if 'risk_management' not in self.config:
                        self.config['risk_management'] = {}
                    self.config['risk_management']['default_stop_loss'] = stop_loss
                
                logger.info(f"[CONFIG] Stop loss set to {stop_loss}%")
                return jsonify({
                    'success': True,
                    'stop_loss': stop_loss,
                    'message': f'Stop loss updated to {stop_loss}%'
                })
            except Exception as e:
                logger.error(f"Error setting stop loss: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @app.route('/api/force_trade', methods=['POST'])
        def force_trade():
            """Execute a forced trade (BUY or SELL)"""
            try:
                data = request.get_json()
                action = data.get('action', '').upper()
                symbol = data.get('symbol', '').upper()
                
                if not symbol:
                    return jsonify({'success': False, 'error': 'Symbol required'}), 400
                
                if action not in ['BUY', 'SELL']:
                    return jsonify({'success': False, 'error': 'Action must be BUY or SELL'}), 400
                
                confidence = float(data.get('confidence', 65))
                stop_loss = float(data.get('stop_loss', 10))
                
                logger.info(f"[FORCE TRADE] {action} {symbol} - Confidence: {confidence}%, Stop Loss: {stop_loss}%")
                
                if action == 'BUY':
                    result = self.engine.execute_force_buy(symbol, confidence, stop_loss)
                else:
                    result = self.engine.execute_force_sell(symbol)
                
                if result:
                    return jsonify({
                        'success': True,
                        'action': action,
                        'symbol': symbol,
                        'message': f'{action} order executed for {symbol}',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({'success': False, 'error': f'Failed to execute {action} for {symbol}'}), 500
                    
            except Exception as e:
                logger.error(f"Error in force trade: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @app.route('/api/get_config', methods=['GET'])
        def get_config():
            """Get current trading configuration"""
            try:
                config = {
                    'confidence': self.config.get('trading', {}).get('min_confidence', 65),
                    'stop_loss': self.config.get('risk_management', {}).get('default_stop_loss', 10),
                }
                return jsonify({'success': True, 'config': config})
            except Exception as e:
                logger.error(f"Error getting config: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        return app  ← KEEP THIS LINE
```

---

## 🧪 HOW TO TEST

After adding the routes, test them:

### Start Platform:
```cmd
cd C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
python unified_trading_platform.py --paper-trading
```

### Test API Endpoints:

**1. Set Confidence:**
```cmd
curl -X POST http://localhost:5000/api/set_confidence -H "Content-Type: application/json" -d "{\"confidence\": 75}"
```

**2. Set Stop Loss:**
```cmd
curl -X POST http://localhost:5000/api/set_stop_loss -H "Content-Type: application/json" -d "{\"stop_loss\": 8}"
```

**3. Force BUY:**
```cmd
curl -X POST http://localhost:5000/api/force_trade -H "Content-Type: application/json" -d "{\"action\": \"BUY\", \"symbol\": \"BHP.AX\", \"confidence\": 75, \"stop_loss\": 8}"
```

**4. Force SELL:**
```cmd
curl -X POST http://localhost:5000/api/force_trade -H "Content-Type: application/json" -d "{\"action\": \"SELL\", \"symbol\": \"BHP.AX\"}"
```

---

## 📋 SUMMARY

**What's Already Done** (in sandbox file):
- ✅ `execute_force_buy()` method added
- ✅ `execute_force_sell()` method added
- ✅ Backup created (`.backup_v87`)

**What You Need to Add** (manually or download):
- ❌ API routes `/api/set_confidence`
- ❌ API routes `/api/set_stop_loss`
- ❌ API routes `/api/force_trade`
- ❌ API routes `/api/get_config`

**Where to Add**:
- Inside `_setup_dashboard()` method
- Just BEFORE the `return app` line (around line 627)

---

## 🎯 EASIEST SOLUTION

**Would you like me to:**
1. Show you the complete updated `unified_trading_platform.py` file contents?
2. Create a simple Python script that patches it automatically?
3. Just give you the 4 route functions to copy/paste?

Let me know which option you prefer! 🚀

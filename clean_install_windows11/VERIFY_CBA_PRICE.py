#!/usr/bin/env python3
"""
Verify CBA.AX shows real market price (~$170)
Remove any hardcoded $100 values
"""

import os
import re
import yfinance as yf

def check_real_cba_price():
    """Get the real CBA.AX price from Yahoo Finance"""
    try:
        ticker = yf.Ticker("CBA.AX")
        hist = ticker.history(period="1d")
        if not hist.empty:
            real_price = hist['Close'].iloc[-1]
            print(f"✓ Real CBA.AX price from Yahoo Finance: ${real_price:.2f}")
            return real_price
        else:
            print("! Unable to fetch CBA.AX price - market may be closed")
            return None
    except Exception as e:
        print(f"! Error fetching price: {e}")
        return None

def fix_hardcoded_prices():
    """Remove any hardcoded $100 values for CBA"""
    files_to_check = [
        "backend.py",
        "backend_ml_fixed.py",
        "backend_ml_enhanced.py",
        "index.html"
    ]
    
    # Add module files
    if os.path.exists("modules"):
        for module in os.listdir("modules"):
            if module.endswith(".html"):
                files_to_check.append(os.path.join("modules", module))
    
    fixed_count = 0
    
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        original_content = content
        
        # Remove hardcoded CBA prices around 100
        patterns = [
            # Python files
            (r"'CBA\.AX':\s*\{\s*'price':\s*100[^}]*\}", ""),
            (r"if\s+symbol\s*==\s*['\"]CBA\.AX['\"]:?\s*price\s*=\s*100", ""),
            (r"default_price\s*=\s*100", "default_price = None"),
            
            # JavaScript
            (r"price:\s*100[,\s]*//.*CBA", ""),
            (r"currentPrice:\s*100", ""),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            fixed_count += 1
            print(f"✓ Fixed hardcoded prices in {filepath}")
    
    if fixed_count == 0:
        print("✓ No hardcoded $100 prices found")
    
    return fixed_count

def verify_backend_returns_real_data():
    """Check that backend.py properly fetches real data"""
    if not os.path.exists("backend.py"):
        print("! backend.py not found")
        return
    
    with open("backend.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check for proper yfinance usage
    if "yfinance" in content and "ticker.history" in content:
        print("✓ Backend uses yfinance to fetch real data")
    else:
        print("! Backend may not be using yfinance properly")
    
    # Check for fallback data
    if "synthetic" in content.lower() or "demo" in content.lower() or "fallback" in content.lower():
        # Check if it's in comments or error messages
        lines_with_fallback = [line for line in content.split('\n') 
                               if ('synthetic' in line.lower() or 'demo' in line.lower() or 'fallback' in line.lower())
                               and not line.strip().startswith('#')]
        
        if lines_with_fallback:
            print(f"! Found {len(lines_with_fallback)} lines with fallback/synthetic/demo references")
            for line in lines_with_fallback[:3]:  # Show first 3
                print(f"  Line: {line.strip()[:80]}...")
        else:
            print("✓ No active fallback data found (only in comments)")
    else:
        print("✓ No fallback/synthetic/demo data references found")

def create_cba_test_html():
    """Create a simple HTML page to test CBA price"""
    test_html = '''<!DOCTYPE html>
<html>
<head>
    <title>CBA.AX Price Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        .price-box {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .price {
            font-size: 48px;
            font-weight: bold;
            color: #4CAF50;
        }
        .error {
            color: #f44336;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <h1>CBA.AX Real Price Test</h1>
    
    <div class="price-box">
        <h2>Testing Backend API</h2>
        <div id="backend-result">Loading...</div>
    </div>
    
    <div class="price-box">
        <h2>Testing ML Backend</h2>
        <div id="ml-result">Loading...</div>
    </div>
    
    <button onclick="testAll()">Refresh Tests</button>
    
    <script>
        async function testBackend() {
            const resultDiv = document.getElementById('backend-result');
            try {
                const response = await fetch('http://localhost:8002/api/stock/CBA.AX');
                const data = await response.json();
                
                if (response.ok && data.price) {
                    const price = parseFloat(data.price);
                    if (price < 120) {
                        resultDiv.innerHTML = `<span class="error">ERROR: Price too low!</span><br>CBA.AX: <span class="price">$${price.toFixed(2)}</span>`;
                    } else {
                        resultDiv.innerHTML = `CBA.AX: <span class="price">$${price.toFixed(2)}</span><br>✓ Real market price`;
                    }
                } else {
                    resultDiv.innerHTML = `<span class="error">Error: ${data.detail || 'Failed to fetch'}</span>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<span class="error">Backend not responding: ${error.message}</span>`;
            }
        }
        
        async function testML() {
            const resultDiv = document.getElementById('ml-result');
            try {
                const response = await fetch('http://localhost:8003/api/ml/predict', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        symbol: 'CBA.AX',
                        timeframe: '5d',
                        models: ['lstm']
                    })
                });
                const data = await response.json();
                
                if (response.ok && data.current_price) {
                    const price = parseFloat(data.current_price);
                    if (price < 120) {
                        resultDiv.innerHTML = `<span class="error">ERROR: Price too low!</span><br>Current: <span class="price">$${price.toFixed(2)}</span>`;
                    } else {
                        resultDiv.innerHTML = `Current: <span class="price">$${price.toFixed(2)}</span><br>✓ Using real data`;
                    }
                } else {
                    resultDiv.innerHTML = `<span class="error">Error: ${data.detail || 'Failed to predict'}</span>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<span class="error">ML Backend not responding: ${error.message}</span>`;
            }
        }
        
        async function testAll() {
            document.getElementById('backend-result').innerHTML = 'Testing...';
            document.getElementById('ml-result').innerHTML = 'Testing...';
            await testBackend();
            await testML();
        }
        
        // Run tests on load
        testAll();
    </script>
</body>
</html>'''
    
    with open("TEST_CBA_PRICE.html", "w", encoding="utf-8") as f:
        f.write(test_html)
    
    print("✓ Created TEST_CBA_PRICE.html")

def main():
    print("=" * 60)
    print("CBA.AX Price Verification")
    print("=" * 60)
    
    # Check real price
    real_price = check_real_cba_price()
    
    # Fix hardcoded prices
    print("\nFixing hardcoded prices...")
    fix_hardcoded_prices()
    
    # Verify backend
    print("\nVerifying backend configuration...")
    verify_backend_returns_real_data()
    
    # Create test page
    print("\nCreating test page...")
    create_cba_test_html()
    
    print("\n" + "=" * 60)
    print("Verification Complete!")
    print("=" * 60)
    
    if real_price:
        if real_price > 150:
            print(f"✓ CBA.AX real price is ${real_price:.2f} (correct range)")
        else:
            print(f"! Warning: CBA.AX price ${real_price:.2f} seems low")
    
    print("\nTo test CBA.AX price display:")
    print("1. Start all services with START_STOCK_TRACKER.bat")
    print("2. Open TEST_CBA_PRICE.html in your browser")
    print("3. Check that price shows ~$170, not $100")

if __name__ == "__main__":
    main()
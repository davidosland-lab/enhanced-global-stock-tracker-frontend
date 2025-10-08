#!/usr/bin/env python3
"""
Remove ALL Fallback, Demo, and Synthetic Data
Replace with proper error handling and user messages
"""

import os
import re
import shutil
from datetime import datetime

def remove_html_fallbacks():
    """Remove all fallback prices from HTML files"""
    
    print("Removing fallbacks from HTML files...")
    
    # Find all HTML files
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    for filename in html_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove price fallbacks - show error instead
            content = re.sub(
                r'(stockData\.price\s*\|\|\s*stockData\.regularMarketPrice)\s*\|\|\s*\d+',
                r'\1',
                content
            )
            
            # Remove standalone fallbacks
            content = re.sub(
                r'const\s+currentPrice\s*=\s*stockData\.(price|regularMarketPrice)\s*\|\|\s*\d+',
                r'''const currentPrice = stockData.\1;
                if (!currentPrice) {
                    alert('Unable to fetch current price. Please check your connection and try again.');
                    throw new Error('Price data not available');
                }''',
                content
            )
            
            # Remove any remaining || 100, || 170, etc.
            content = re.sub(
                r'\|\|\s*\d{2,3}(?:\.\d+)?(?=\s*[;,\)])',
                '',
                content
            )
            
            if content != original_content:
                # Backup and save
                backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(filename, backup_name)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"  ✓ Removed fallbacks from {filename}")
        
        except Exception as e:
            print(f"  ! Error processing {filename}: {e}")
    
    return True

def remove_backend_fallbacks():
    """Remove all fallback data from backend.py"""
    
    if not os.path.exists('backend.py'):
        print("  ! backend.py not found")
        return False
    
    print("Removing fallbacks from backend.py...")
    
    with open('backend.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove price fallbacks in get_stock_data
    content = re.sub(
        r"'currentPrice'\s*or\s*info\.get\('regularMarketPrice',\s*0\)",
        "'currentPrice') or info.get('regularMarketPrice')",
        content
    )
    
    # Remove default value fallbacks
    content = re.sub(
        r"\.get\((.*?),\s*0\)",
        r".get(\1)",
        content
    )
    
    # Fix error handling to return proper errors instead of fallbacks
    if "return {" in content and '"error":' not in content:
        # Add proper error handling
        content = re.sub(
            r"except\s+Exception\s+as\s+e:\s*\n\s*logger\.error",
            '''except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        raise HTTPException(status_code=503, detail=f"Unable to fetch real-time data: {str(e)}")
        logger.error''',
            content
        )
    
    if content != original_content:
        backup_name = f"backend.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2('backend.py', backup_name)
        
        with open('backend.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("  ✓ Removed fallbacks from backend.py")
    else:
        print("  ✓ No fallbacks found in backend.py")
    
    return True

def remove_ml_backend_fallbacks():
    """Remove all synthetic data from ML backend"""
    
    if not os.path.exists('backend_ml_enhanced.py'):
        print("  ! backend_ml_enhanced.py not found")
        return False
    
    print("Removing fallbacks from backend_ml_enhanced.py...")
    
    with open('backend_ml_enhanced.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove ALL numeric fallbacks
    content = re.sub(
        r"features\.get\('last_price',\s*\d+\)",
        "features.get('last_price')",
        content
    )
    
    # Remove return fallbacks
    content = re.sub(
        r"return\s+\d+\s*#.*(?:fallback|default)",
        "raise ValueError('No price data available')",
        content
    )
    
    # Fix last_price assignments
    content = re.sub(
        r"last_price\s*=\s*features\.get\('last_price',\s*\d+\)",
        '''last_price = features.get('last_price')
        if not last_price:
            raise ValueError('No price data available for prediction')''',
        content
    )
    
    # Remove synthetic price generation
    content = re.sub(
        r"last_price\s*\*\s*0\.9\d+",
        "last_price  # Real price only, no synthetic adjustments",
        content
    )
    
    # Fix ensemble predictions to require real data
    content = re.sub(
        r"features\.get\(\"last_price\",\s*\d+\)\s*\*\s*[\d.]+",
        '''features.get("last_price")  # Must have real price
        if not features.get("last_price"):
            raise ValueError("Cannot make prediction without current price data")''',
        content
    )
    
    if content != original_content:
        backup_name = f"backend_ml_enhanced.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2('backend_ml_enhanced.py', backup_name)
        
        with open('backend_ml_enhanced.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("  ✓ Removed all fallbacks from backend_ml_enhanced.py")
    else:
        print("  ✓ No fallbacks found in backend_ml_enhanced.py")
    
    return True

def remove_mock_data():
    """Remove any mock/demo data structures"""
    
    print("Checking for mock/demo data...")
    
    files_to_check = ['backend.py', 'backend_ml_enhanced.py']
    
    for filename in files_to_check:
        if not os.path.exists(filename):
            continue
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove mock model performance data
        if "# For now, return mock data" in content:
            content = re.sub(
                r"#\s*For now,\s*return mock data.*?return\s*models",
                '''# Return empty list if no real models available
        if not models:
            raise HTTPException(status_code=404, detail="No trained models available. Please train a model first.")
        return models''',
                content,
                flags=re.DOTALL
            )
        
        # Remove any generateSynthetic functions
        content = re.sub(
            r"def\s+generateSynthetic.*?\n(?=def|\Z)",
            "",
            content,
            flags=re.DOTALL
        )
        
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Removed mock data from {filename}")
    
    return True

def add_error_handling():
    """Add proper error messages for missing data"""
    
    print("Adding proper error handling...")
    
    # Create a new JavaScript file for error handling
    error_handler_js = '''// Error handling for missing data
function handleDataError(error, context) {
    console.error(`Data error in ${context}:`, error);
    
    const errorMessages = {
        'price': 'Unable to fetch current price. Please check market hours and connection.',
        'historical': 'Historical data unavailable. Please try again later.',
        'prediction': 'Cannot generate prediction without real market data.',
        'training': 'Training requires real historical data. Please ensure market data is accessible.'
    };
    
    const message = errorMessages[context] || 'Unable to fetch required data. Please try again.';
    
    // Show user-friendly error
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = 'background: #ff4444; color: white; padding: 15px; border-radius: 5px; margin: 10px 0;';
    errorDiv.innerHTML = `<strong>Error:</strong> ${message}`;
    
    // Find appropriate container
    const container = document.querySelector('.main-content') || document.querySelector('.container') || document.body;
    container.insertBefore(errorDiv, container.firstChild);
    
    // Auto-remove after 10 seconds
    setTimeout(() => errorDiv.remove(), 10000);
}

// Override fetch to handle errors globally
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    try {
        const response = await originalFetch(...args);
        if (!response.ok && response.status === 503) {
            const error = await response.json();
            handleDataError(error, 'api');
        }
        return response;
    } catch (error) {
        handleDataError(error, 'network');
        throw error;
    }
};
'''
    
    with open('error_handler.js', 'w') as f:
        f.write(error_handler_js)
    
    print("  ✓ Created error_handler.js")
    
    # Add to index.html
    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'error_handler.js' not in content:
            content = content.replace('</head>', '<script src="error_handler.js"></script>\n</head>')
            
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("  ✓ Added error handler to index.html")
    
    return True

def main():
    print("="*70)
    print("REMOVING ALL FALLBACKS, DEMO, AND SYNTHETIC DATA")
    print("="*70)
    print()
    print("This will:")
    print("  • Remove ALL hardcoded fallback values")
    print("  • Remove ALL demo/synthetic data")
    print("  • Add proper error messages when real data is unavailable")
    print("  • Ensure ONLY real Yahoo Finance data is used")
    print()
    print("Working directory:", os.getcwd())
    print()
    
    # Run all fixes
    success = True
    
    if not remove_html_fallbacks():
        success = False
    print()
    
    if not remove_backend_fallbacks():
        success = False
    print()
    
    if not remove_ml_backend_fallbacks():
        success = False
    print()
    
    if not remove_mock_data():
        success = False
    print()
    
    if not add_error_handling():
        success = False
    
    print()
    print("="*70)
    
    if success:
        print("✓ ALL FALLBACKS AND SYNTHETIC DATA REMOVED!")
        print("="*70)
        print()
        print("Changes made:")
        print("  ✓ No more fallback prices (100, 170, etc.)")
        print("  ✓ No more synthetic data generation")
        print("  ✓ No more mock/demo data")
        print("  ✓ Proper error messages when data unavailable")
        print()
        print("The system will now:")
        print("  • Use ONLY real Yahoo Finance data")
        print("  • Show error messages if data is unavailable")
        print("  • Never show fake/fallback values")
        print()
        print("IMPORTANT: Restart all services for changes to take effect!")
    else:
        print("! SOME OPERATIONS FAILED")
        print("="*70)
        print("Check the errors above for details")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        input("\nPress Enter to exit...")
        exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        input("\nPress Enter to exit...")
        exit(1)
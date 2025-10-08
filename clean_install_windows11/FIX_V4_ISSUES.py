#!/usr/bin/env python3
"""
Fix issues introduced in v4.0 Real Data Only version
- Add missing /api/health endpoint
- Fix ML backend startup
- Fix error handler issues
"""

import os
import shutil
from datetime import datetime

def add_health_endpoint_to_backend():
    """Add /api/health endpoint to backend.py"""
    
    print("Adding /api/health endpoint to backend.py...")
    
    if not os.path.exists('backend.py'):
        print("  ! backend.py not found")
        return False
    
    with open('backend.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if health endpoint already exists
    if '/api/health' in content or '@app.get("/health")' in content:
        print("  ✓ Health endpoint already exists")
        return True
    
    # Create backup
    backup_name = f"backend.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2('backend.py', backup_name)
    print(f"  Created backup: {backup_name}")
    
    # Find where to insert the health endpoint (after the root endpoint)
    health_endpoint = '''
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Stock Tracker Backend",
        "timestamp": datetime.now().isoformat()
    }
'''
    
    # Insert after the first endpoint definition or after app creation
    if '@app.get("/")' in content:
        content = content.replace('@app.get("/")', health_endpoint + '\n@app.get("/")')
    elif 'app = FastAPI' in content:
        # Find the first route and insert before it
        import_end = content.find('@app.')
        if import_end > 0:
            content = content[:import_end] + health_endpoint + '\n' + content[import_end:]
    
    # Save the fixed file
    with open('backend.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✓ Added /api/health endpoint to backend.py")
    return True

def fix_error_handler():
    """Fix the overly aggressive error handler"""
    
    print("Fixing error_handler.js...")
    
    if not os.path.exists('error_handler.js'):
        print("  ! error_handler.js not found")
        return True  # Not a critical error
    
    # Create a less aggressive version
    new_error_handler = '''// Error handling for missing data - Fixed version
function handleDataError(error, context) {
    // Only log to console, don't show popups for every error
    console.warn(`Data issue in ${context}:`, error.message || error);
    
    // Only show user message for critical errors, not health checks
    if (context === 'critical' || (error.message && error.message.includes('Real data not available'))) {
        const errorMessages = {
            'price': 'Unable to fetch current price. Please check market hours and connection.',
            'historical': 'Historical data unavailable. Please try again later.',
            'prediction': 'Cannot generate prediction without real market data.',
            'training': 'Training requires real historical data. Please ensure market data is accessible.'
        };
        
        const message = errorMessages[context] || 'Unable to fetch required data. Please try again.';
        
        // Show user-friendly error only for critical issues
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = 'background: #ff4444; color: white; padding: 15px; border-radius: 5px; margin: 10px 0;';
        errorDiv.innerHTML = `<strong>Error:</strong> ${message}`;
        
        const container = document.querySelector('.main-content') || document.querySelector('.container') || document.body;
        if (container && container.querySelector) {
            container.insertBefore(errorDiv, container.firstChild);
            setTimeout(() => errorDiv.remove(), 10000);
        }
    }
}

// Don't override fetch globally - it causes too many issues
// Only handle critical errors
window.handleCriticalError = handleDataError;
'''
    
    # Create backup and replace
    backup_name = f"error_handler.js.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2('error_handler.js', backup_name)
    
    with open('error_handler.js', 'w') as f:
        f.write(new_error_handler)
    
    print("  ✓ Fixed error_handler.js to be less aggressive")
    return True

def ensure_ml_backend_starts():
    """Create a reliable ML backend startup script"""
    
    print("Creating ML backend startup fix...")
    
    ml_startup = '''@echo off
echo Starting ML Backend on port 8003...
if exist backend_ml_enhanced.py (
    python backend_ml_enhanced.py
) else (
    echo ERROR: backend_ml_enhanced.py not found!
    echo Please ensure all files are extracted from the zip.
    pause
)
'''
    
    with open('START_ML_BACKEND.bat', 'w') as f:
        f.write(ml_startup)
    
    print("  ✓ Created START_ML_BACKEND.bat")
    return True

def fix_index_html():
    """Fix index.html to handle missing endpoints gracefully"""
    
    print("Fixing index.html...")
    
    if not os.path.exists('index.html'):
        print("  ! index.html not found")
        return False
    
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_name = f"index.html.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2('index.html', backup_name)
    
    # Fix the checkSystemStatus function to handle errors better
    old_check = "const response = await fetch(`${API_BASE}/api/health`);"
    new_check = '''const response = await fetch(`${API_BASE}/api/health`).catch(err => {
                    console.log('Backend health check failed, trying alternative endpoint');
                    return fetch(`${API_BASE}/`);
                });'''
    
    if old_check in content:
        content = content.replace(old_check, new_check)
        print("  ✓ Fixed backend health check")
    
    # Fix ML backend health check
    old_ml_check = "const response = await fetch(`${ML_API_BASE}/health`);"
    new_ml_check = '''const response = await fetch(`${ML_API_BASE}/health`).catch(err => {
                    console.log('ML Backend not available');
                    return null;
                });'''
    
    if old_ml_check in content:
        content = content.replace(old_ml_check, new_ml_check)
        print("  ✓ Fixed ML backend health check")
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("="*60)
    print("FIXING V4.0 ISSUES")
    print("="*60)
    print()
    print("This will fix:")
    print("  • Missing /api/health endpoint (404 error)")
    print("  • ML Backend connection refused")
    print("  • Overly aggressive error handling")
    print()
    
    success = True
    
    # Apply all fixes
    if not add_health_endpoint_to_backend():
        success = False
    print()
    
    if not fix_error_handler():
        success = False
    print()
    
    if not ensure_ml_backend_starts():
        success = False
    print()
    
    if not fix_index_html():
        success = False
    
    print()
    print("="*60)
    
    if success:
        print("✓ V4.0 ISSUES FIXED!")
        print("="*60)
        print()
        print("Next steps:")
        print("  1. Restart all services")
        print("  2. Make sure ML Backend is running (port 8003)")
        print("  3. Refresh browser (Ctrl+F5)")
        print()
        print("To start services:")
        print("  • Run INSTALL.bat again, or")
        print("  • Run START_ALL_SERVICES_FIXED.bat")
    else:
        print("! Some fixes failed")
        print("="*60)
    
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
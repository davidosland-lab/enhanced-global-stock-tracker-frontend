#!/usr/bin/env python3
"""
Browser launcher for GSMT
Opens the tracker in the default web browser
"""

import webbrowser
import os
import sys
import time

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the HTML file
    html_file = os.path.join(script_dir, 'frontend', 'indices_tracker_market_hours.html')
    
    # Convert to file:// URL format
    if os.name == 'nt':  # Windows
        # Replace backslashes with forward slashes for URL
        html_file = html_file.replace('\\', '/')
        # Add file:/// prefix
        url = f'file:///{html_file}'
    else:
        url = f'file://{html_file}'
    
    print(f"Opening GSMT in browser...")
    print(f"URL: {url}")
    
    # Try multiple methods to open the browser
    try:
        # Method 1: Use default browser
        webbrowser.open(url, new=2)  # new=2 opens in new tab
        print("✓ Browser opened successfully!")
        return True
    except:
        pass
    
    # Method 2: Try specific browsers
    browsers = [
        'chrome',
        'firefox', 
        'edge',
        'windows-default'
    ]
    
    for browser_name in browsers:
        try:
            browser = webbrowser.get(browser_name)
            browser.open(url, new=2)
            print(f"✓ Opened with {browser_name}")
            return True
        except:
            continue
    
    # If all else fails, print the URL for manual opening
    print("\n" + "="*60)
    print("Could not open browser automatically.")
    print("Please open your browser and navigate to:")
    print(f"\n{url}")
    print("="*60)
    return False

if __name__ == "__main__":
    main()
    # Keep console open for a moment
    time.sleep(2)
#!/usr/bin/env python3
"""
Toggle sentiment analysis on/off
Quick utility to enable/disable sentiment without editing code
"""

import sys

def toggle_sentiment(enable=None):
    """Toggle or set sentiment analysis state"""
    
    # Read current config
    try:
        with open('ml_config.py', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("Error: ml_config.py not found!")
        return
    
    # Find the sentiment line
    for i, line in enumerate(lines):
        if 'USE_SENTIMENT_ANALYSIS' in line and '=' in line:
            current = 'True' in line
            
            if enable is None:
                # Toggle
                new_state = not current
            else:
                # Set specific state
                new_state = enable
            
            # Update the line
            lines[i] = f"USE_SENTIMENT_ANALYSIS = {new_state}\n"
            
            # Write back
            with open('ml_config.py', 'w') as f:
                f.writelines(lines)
            
            print(f"✅ Sentiment analysis {'ENABLED' if new_state else 'DISABLED'}")
            print(f"   Previous state: {'Enabled' if current else 'Disabled'}")
            print(f"   New state: {'Enabled' if new_state else 'Disabled'}")
            
            if new_state:
                print("\n⚠️  WARNING: Sentiment analysis makes 20+ Yahoo Finance API calls")
                print("   This may cause rate limiting and connection failures.")
                print("   Consider using the fixed batch version instead.")
            else:
                print("\n✅ Yahoo Finance connection should work properly now.")
                print("   The system will use 35 technical features (without sentiment).")
            
            return
    
    print("Error: USE_SENTIMENT_ANALYSIS setting not found in ml_config.py")

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['on', 'enable', 'true', '1']:
            toggle_sentiment(True)
        elif arg in ['off', 'disable', 'false', '0']:
            toggle_sentiment(False)
        elif arg in ['toggle']:
            toggle_sentiment(None)
        else:
            print("Usage: python toggle_sentiment.py [on|off|toggle]")
            print("  on/enable/true/1  - Enable sentiment analysis")
            print("  off/disable/false/0 - Disable sentiment analysis")
            print("  toggle - Toggle current state")
            print("  (no argument) - Show current state")
    else:
        # Show current state
        try:
            with open('ml_config.py', 'r') as f:
                content = f.read()
                if 'USE_SENTIMENT_ANALYSIS = True' in content:
                    print("Sentiment analysis is currently: ENABLED ⚠️")
                    print("This may cause Yahoo Finance connection issues.")
                elif 'USE_SENTIMENT_ANALYSIS = False' in content:
                    print("Sentiment analysis is currently: DISABLED ✅")
                    print("Yahoo Finance should work properly.")
                else:
                    print("Could not determine sentiment analysis state")
        except FileNotFoundError:
            print("Error: ml_config.py not found!")

if __name__ == "__main__":
    main()
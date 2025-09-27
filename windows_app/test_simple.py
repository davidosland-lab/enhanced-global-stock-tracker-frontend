#!/usr/bin/env python3
"""
Simple test to verify Python is working
"""

import sys
import os

print("=" * 50)
print("Python Installation Test")
print("=" * 50)
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Current Directory: {os.getcwd()}")
print(f"Script Location: {os.path.abspath(__file__)}")
print("=" * 50)

# Test if we can create a simple window
try:
    import tkinter as tk
    print("✓ tkinter (GUI) is available")
    
    # Create a test window
    root = tk.Tk()
    root.title("Python Test - Success!")
    root.geometry("400x200")
    
    label = tk.Label(root, text="Python is working correctly!\n\nStock Predictor Pro can run.", 
                     font=("Arial", 14))
    label.pack(pady=50)
    
    button = tk.Button(root, text="Close", command=root.quit, width=20, height=2)
    button.pack()
    
    print("✓ Opening test window...")
    root.mainloop()
    
except ImportError:
    print("✗ tkinter not available - GUI won't work")
    input("\nPress Enter to exit...")
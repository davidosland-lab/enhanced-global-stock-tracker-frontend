#!/usr/bin/env python
"""
Stock Predictor Pro - Minimal Version
This version has NO external dependencies - only uses Python standard library
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import sys
import os
from datetime import datetime

class StockPredictorMinimal:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("Stock Predictor Pro - Minimal")
        self.root.geometry("800x600")
        
        # Center window
        self.center_window()
        
        # Create UI
        self.create_ui()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(main_frame, text="📈 Stock Predictor Pro", 
                        font=('Arial', 20, 'bold'), fg='blue')
        title.pack(pady=10)
        
        # Version info
        version_info = tk.Label(main_frame, 
                               text=f"Minimal Version | Python {sys.version.split()[0]}",
                               font=('Arial', 10))
        version_info.pack()
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Stock Prediction", padding="10")
        input_frame.pack(fill=tk.X, pady=20)
        
        # Symbol input
        symbol_frame = ttk.Frame(input_frame)
        symbol_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(symbol_frame, text="Symbol:").pack(side=tk.LEFT, padx=5)
        self.symbol_var = tk.StringVar(value="AAPL")
        self.symbol_entry = ttk.Entry(symbol_frame, textvariable=self.symbol_var, width=10)
        self.symbol_entry.pack(side=tk.LEFT, padx=5)
        
        # Timeframe
        ttk.Label(symbol_frame, text="Timeframe:").pack(side=tk.LEFT, padx=5)
        self.timeframe_var = tk.StringVar(value="1 Week")
        timeframe_combo = ttk.Combobox(symbol_frame, textvariable=self.timeframe_var,
                                      values=["1 Day", "1 Week", "1 Month", "3 Months", "1 Year"],
                                      width=12, state="readonly")
        timeframe_combo.pack(side=tk.LEFT, padx=5)
        
        # Predict button
        predict_btn = tk.Button(symbol_frame, text="Generate Prediction", 
                              command=self.generate_prediction,
                              bg='green', fg='white', font=('Arial', 10, 'bold'),
                              padx=20, pady=5)
        predict_btn.pack(side=tk.LEFT, padx=20)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Prediction Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Results text
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=15, width=70)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.results_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Menu bar
        self.create_menu()
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Results", command=self.clear_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Test Python", command=self.test_python)
        
    def generate_prediction(self):
        """Generate a simulated prediction"""
        symbol = self.symbol_var.get().upper()
        timeframe = self.timeframe_var.get()
        
        if not symbol:
            messagebox.showwarning("Input Error", "Please enter a stock symbol")
            return
        
        self.status_var.set(f"Generating prediction for {symbol}...")
        self.root.update()
        
        # Simulate some processing
        self.root.after(500, lambda: self.show_prediction(symbol, timeframe))
        
    def show_prediction(self, symbol, timeframe):
        """Show prediction results"""
        # Generate random prediction data
        current_price = round(random.uniform(50, 500), 2)
        change_percent = round(random.uniform(-10, 10), 2)
        predicted_price = round(current_price * (1 + change_percent/100), 2)
        confidence = round(random.uniform(60, 95), 1)
        
        # Determine recommendation
        if change_percent > 2:
            recommendation = "STRONG BUY"
            color = "green"
        elif change_percent > 0:
            recommendation = "BUY"
            color = "lightgreen"
        elif change_percent > -2:
            recommendation = "HOLD"
            color = "yellow"
        else:
            recommendation = "SELL"
            color = "red"
        
        # Generate results text
        results = f"""
{'='*60}
PREDICTION RESULTS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

Stock Symbol: {symbol}
Timeframe: {timeframe}
Analysis Type: Technical + Sentiment

CURRENT STATUS:
---------------
Current Price: ${current_price}
24h Volume: {random.randint(1000000, 50000000):,}
Market Cap: ${random.randint(1, 500)}B

PREDICTION:
-----------
Predicted Price: ${predicted_price}
Expected Change: {change_percent:+.2f}%
Confidence Level: {confidence}%

TECHNICAL INDICATORS:
--------------------
RSI (14): {random.randint(30, 70)}
MACD: {'Bullish' if change_percent > 0 else 'Bearish'}
Moving Avg (50): ${round(current_price * 0.98, 2)}
Moving Avg (200): ${round(current_price * 0.95, 2)}

RECOMMENDATION: {recommendation}

Risk Level: {'Low' if abs(change_percent) < 3 else 'Medium' if abs(change_percent) < 7 else 'High'}

{'='*60}
Note: This is a simulated prediction for demonstration.
In production, this would use real ML models and market data.
{'='*60}
"""
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results)
        
        self.status_var.set(f"Prediction complete for {symbol}")
        
    def clear_results(self):
        """Clear the results text"""
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Results cleared")
        
    def show_about(self):
        """Show about dialog"""
        about_text = f"""Stock Predictor Pro - Minimal Version

Version: 1.0.0 (Minimal)
Python: {sys.version.split()[0]}

This is a minimal version that works with
only Python's standard library - no external
packages required!

Features:
• Stock prediction simulation
• Technical indicators
• Risk assessment
• Clean, simple interface

© 2024 Stock Predictor Team"""
        
        messagebox.showinfo("About", about_text)
        
    def test_python(self):
        """Test Python installation"""
        test_info = f"""Python Installation Test
{'='*30}

Python Version: {sys.version}
Executable: {sys.executable}
Platform: {sys.platform}
Current Dir: {os.getcwd()}

✓ Python is working correctly!
✓ Tkinter (GUI) is available!
✓ Application can run!

Everything is OK!"""
        
        messagebox.showinfo("Python Test", test_info)
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("Starting Stock Predictor Pro (Minimal)...")
    print(f"Python {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        app = StockPredictorMinimal()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        # Show error in console and message box
        error_msg = f"Failed to start application:\n{str(e)}"
        try:
            tk.Tk().withdraw()
            messagebox.showerror("Startup Error", error_msg)
        except:
            print(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
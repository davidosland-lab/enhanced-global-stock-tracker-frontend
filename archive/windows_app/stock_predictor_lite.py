#!/usr/bin/env python3
"""
Stock Predictor Pro - Lightweight Version
A simplified version that works with minimal dependencies
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
import sys
from datetime import datetime, timedelta
import queue

# Check for optional imports
HAS_REQUESTS = False
HAS_NUMPY = False
HAS_CUSTOM_TK = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    pass

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    pass

try:
    import customtkinter as ctk
    HAS_CUSTOM_TK = True
except ImportError:
    pass


class StockPredictorLite:
    """Lightweight Stock Predictor Application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stock Predictor Pro - Lite Version")
        self.root.geometry("1200x700")
        
        # Try to set dark theme if possible
        try:
            self.root.tk.call('source', 'azure.tcl')
            self.root.tk.call('set_theme', 'dark')
        except:
            pass
        
        # Configuration
        self.cloud_api = "https://8000-sandbox.e2b.dev"
        self.data_queue = queue.Queue()
        
        # Setup UI
        self.setup_ui()
        
        # Show status
        self.update_status(f"Stock Predictor Lite - Python {sys.version.split()[0]}")
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="📈 Stock Predictor Pro - Lite", 
                         font=('Arial', 18, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create tabs
        self.create_prediction_tab()
        self.create_settings_tab()
        self.create_about_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def create_prediction_tab(self):
        """Create prediction tab"""
        pred_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(pred_frame, text="Predictions")
        
        # Input section
        input_frame = ttk.LabelFrame(pred_frame, text="Input Parameters", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Symbol input
        ttk.Label(input_frame, text="Symbol:").grid(row=0, column=0, padx=5, pady=5)
        self.symbol_var = tk.StringVar(value="AAPL")
        self.symbol_entry = ttk.Entry(input_frame, textvariable=self.symbol_var, width=15)
        self.symbol_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Timeframe
        ttk.Label(input_frame, text="Timeframe:").grid(row=0, column=2, padx=5, pady=5)
        self.timeframe_var = tk.StringVar(value="1w")
        self.timeframe_combo = ttk.Combobox(input_frame, textvariable=self.timeframe_var, 
                                           values=["1d", "1w", "1m", "3m", "1y"], width=10)
        self.timeframe_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Model
        ttk.Label(input_frame, text="Model:").grid(row=0, column=4, padx=5, pady=5)
        self.model_var = tk.StringVar(value="Simple")
        self.model_combo = ttk.Combobox(input_frame, textvariable=self.model_var,
                                       values=["Simple", "Advanced", "Ensemble"], width=15)
        self.model_combo.grid(row=0, column=5, padx=5, pady=5)
        
        # Predict button
        self.predict_btn = ttk.Button(input_frame, text="Generate Prediction", 
                                    command=self.generate_prediction)
        self.predict_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Results section
        results_frame = ttk.LabelFrame(pred_frame, text="Prediction Results", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        pred_frame.rowconfigure(1, weight=1)
        
        # Results text
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                     width=80, height=20)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(settings_frame, text="Settings")
        
        # API Settings
        api_frame = ttk.LabelFrame(settings_frame, text="API Configuration", padding="10")
        api_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(api_frame, text="Cloud API URL:").grid(row=0, column=0, padx=5, pady=5)
        self.api_var = tk.StringVar(value=self.cloud_api)
        api_entry = ttk.Entry(api_frame, textvariable=self.api_var, width=50)
        api_entry.grid(row=0, column=1, padx=5, pady=5)
        
        test_btn = ttk.Button(api_frame, text="Test Connection", command=self.test_connection)
        test_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Processing Mode
        mode_frame = ttk.LabelFrame(settings_frame, text="Processing Mode", padding="10")
        mode_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.mode_var = tk.StringVar(value="local")
        ttk.Radiobutton(mode_frame, text="Local Processing (Simulated)", 
                       variable=self.mode_var, value="local").grid(row=0, column=0, padx=5, pady=5)
        ttk.Radiobutton(mode_frame, text="Cloud Processing (API)", 
                       variable=self.mode_var, value="cloud").grid(row=0, column=1, padx=5, pady=5)
        
    def create_about_tab(self):
        """Create about tab"""
        about_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(about_frame, text="About")
        
        about_text = f"""
Stock Predictor Pro - Lite Version
===================================

Version: 1.0.0 Lite
Python: {sys.version.split()[0]}

Status:
• Requests library: {'✅ Installed' if HAS_REQUESTS else '❌ Not installed'}
• NumPy library: {'✅ Installed' if HAS_NUMPY else '❌ Not installed'}
• CustomTkinter: {'✅ Installed' if HAS_CUSTOM_TK else '❌ Not installed'}

This is a lightweight version that works with minimal dependencies.
For full features, install all required packages.

Features:
• Basic stock predictions
• Local simulation mode
• Cloud API integration (when available)
• Simple technical analysis

© 2024 Stock Predictor Team
        """
        
        about_label = ttk.Label(about_frame, text=about_text, justify=tk.LEFT)
        about_label.pack()
        
        # Check dependencies button
        check_btn = ttk.Button(about_frame, text="Check Dependencies", 
                             command=self.check_dependencies)
        check_btn.pack(pady=20)
        
    def generate_prediction(self):
        """Generate stock prediction"""
        symbol = self.symbol_var.get()
        timeframe = self.timeframe_var.get()
        model = self.model_var.get()
        mode = self.mode_var.get()
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Generating prediction for {symbol}...\n\n")
        self.update_status(f"Processing {symbol}...")
        
        if mode == "local" or not HAS_REQUESTS:
            # Local simulation
            self.simulate_prediction(symbol, timeframe, model)
        else:
            # Cloud API call
            thread = threading.Thread(target=self.cloud_prediction, 
                                    args=(symbol, timeframe, model))
            thread.daemon = True
            thread.start()
            
    def simulate_prediction(self, symbol, timeframe, model):
        """Simulate a prediction locally"""
        import random
        
        # Simulate processing
        self.root.after(1000, lambda: self._show_simulated_results(symbol, timeframe, model))
        
    def _show_simulated_results(self, symbol, timeframe, model):
        """Show simulated prediction results"""
        import random
        
        current_price = round(random.uniform(100, 200), 2)
        change_pct = random.uniform(-5, 5)
        predicted_price = round(current_price * (1 + change_pct/100), 2)
        confidence = round(random.uniform(0.6, 0.95), 2)
        
        timeframe_map = {
            "1d": "1 Day",
            "1w": "1 Week", 
            "1m": "1 Month",
            "3m": "3 Months",
            "1y": "1 Year"
        }
        
        result_text = f"""
PREDICTION RESULTS
==================
Symbol: {symbol}
Timeframe: {timeframe_map.get(timeframe, timeframe)}
Model: {model}
Mode: Local Simulation

Current Price: ${current_price}
Predicted Price: ${predicted_price}
Expected Change: {change_pct:.2f}%
Confidence: {confidence:.1%}

Recommendation: {'BUY' if predicted_price > current_price else 'SELL'}

Technical Indicators:
• RSI: {random.randint(30, 70)}
• MACD: {'Bullish' if predicted_price > current_price else 'Bearish'}
• Moving Average: ${round(current_price * 0.98, 2)}

Risk Assessment: {'Low' if abs(change_pct) < 2 else 'Medium' if abs(change_pct) < 4 else 'High'}

Note: This is a simulated prediction for demonstration purposes.
"""
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, result_text)
        self.update_status("Prediction complete")
        
    def cloud_prediction(self, symbol, timeframe, model):
        """Get prediction from cloud API"""
        if not HAS_REQUESTS:
            self.root.after(0, lambda: self.results_text.insert(tk.END, 
                "\nError: 'requests' library not installed.\nUsing local simulation instead.\n"))
            self.simulate_prediction(symbol, timeframe, model)
            return
            
        try:
            import requests
            api_url = f"{self.api_var.get()}/api/predict"
            
            payload = {
                "symbol": symbol,
                "timeframe": timeframe,
                "model": model
            }
            
            response = requests.post(api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.root.after(0, lambda: self._show_cloud_results(result))
            else:
                raise Exception(f"API returned status {response.status_code}")
                
        except Exception as e:
            error_msg = f"Cloud API error: {str(e)}\nFalling back to local simulation.\n"
            self.root.after(0, lambda: self.results_text.insert(tk.END, error_msg))
            self.simulate_prediction(symbol, timeframe, model)
            
    def _show_cloud_results(self, result):
        """Display cloud API results"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, json.dumps(result, indent=2))
        self.update_status("Cloud prediction complete")
        
    def test_connection(self):
        """Test cloud API connection"""
        if not HAS_REQUESTS:
            messagebox.showwarning("Missing Dependency", 
                                 "The 'requests' library is not installed.\n"
                                 "Cannot test cloud connection.")
            return
            
        try:
            import requests
            api_url = self.api_var.get()
            response = requests.get(f"{api_url}/health", timeout=5)
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Cloud API connection successful!")
            else:
                messagebox.showwarning("Connection Failed", 
                                     f"API returned status {response.status_code}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            
    def check_dependencies(self):
        """Check installed dependencies"""
        deps_to_check = [
            ("tkinter", "GUI Framework (Built-in)"),
            ("requests", "HTTP Requests"),
            ("numpy", "Numerical Computing"),
            ("pandas", "Data Processing"),
            ("sklearn", "Machine Learning"),
            ("customtkinter", "Modern GUI"),
            ("yfinance", "Stock Data"),
        ]
        
        results = []
        for module, description in deps_to_check:
            try:
                __import__(module)
                results.append(f"✅ {description} ({module})")
            except ImportError:
                results.append(f"❌ {description} ({module})")
                
        result_text = "Dependency Check\n" + "="*40 + "\n" + "\n".join(results)
        messagebox.showinfo("Dependencies", result_text)
        
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(f"{message} | {datetime.now().strftime('%H:%M:%S')}")
        
    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    print(f"Starting Stock Predictor Lite with Python {sys.version}")
    app = StockPredictorLite()
    app.run()


if __name__ == "__main__":
    main()
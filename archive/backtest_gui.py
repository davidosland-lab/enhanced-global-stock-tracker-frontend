#!/usr/bin/env python3
"""
Backtesting GUI - Desktop application for running backtests
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from datetime import datetime, timedelta
import threading

class BacktestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Backtesting System")
        self.root.geometry("800x600")
        
        # API URL
        self.api_url = "https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev"
        
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header = tk.Label(self.root, text="📊 Stock Backtesting System", 
                         font=("Arial", 16, "bold"))
        header.pack(pady=10)
        
        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Backtest Parameters", padding=10)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        # Symbol
        tk.Label(input_frame, text="Symbol:").grid(row=0, column=0, sticky="w", pady=5)
        self.symbol_var = tk.StringVar(value="AAPL")
        tk.Entry(input_frame, textvariable=self.symbol_var, width=10).grid(row=0, column=1, pady=5)
        
        # Start Date
        tk.Label(input_frame, text="Start Date:").grid(row=1, column=0, sticky="w", pady=5)
        self.start_date_var = tk.StringVar(value="2023-01-01")
        tk.Entry(input_frame, textvariable=self.start_date_var, width=15).grid(row=1, column=1, pady=5)
        
        # End Date
        tk.Label(input_frame, text="End Date:").grid(row=2, column=0, sticky="w", pady=5)
        self.end_date_var = tk.StringVar(value="2024-01-01")
        tk.Entry(input_frame, textvariable=self.end_date_var, width=15).grid(row=2, column=1, pady=5)
        
        # Strategy
        tk.Label(input_frame, text="Strategy:").grid(row=3, column=0, sticky="w", pady=5)
        self.strategy_var = tk.StringVar(value="long_only")
        strategy_combo = ttk.Combobox(input_frame, textvariable=self.strategy_var, 
                                      values=["long_only", "long_short", "signals"],
                                      width=12)
        strategy_combo.grid(row=3, column=1, pady=5)
        
        # Buttons Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Run Backtest", command=self.run_backtest,
                 bg="#4CAF50", fg="white", padx=20, pady=10).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Train Models", command=self.train_models,
                 bg="#2196F3", fg="white", padx=20, pady=10).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Clear Results", command=self.clear_results,
                 bg="#f44336", fg="white", padx=20, pady=10).pack(side="left", padx=5)
        
        # Results Frame
        results_frame = ttk.LabelFrame(self.root, text="Results", padding=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=20)
        self.results_text.pack(fill="both", expand=True)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor="w")
        status_bar.pack(fill="x", side="bottom")
    
    def run_backtest(self):
        """Run backtest in a separate thread"""
        thread = threading.Thread(target=self._run_backtest_thread)
        thread.start()
    
    def _run_backtest_thread(self):
        """Thread function for running backtest"""
        self.status_var.set("Running backtest...")
        self.results_text.insert(tk.END, f"\n{'='*50}\n")
        self.results_text.insert(tk.END, f"Running backtest for {self.symbol_var.get()}...\n")
        
        try:
            response = requests.post(
                f"{self.api_url}/api/backtest",
                json={
                    "symbol": self.symbol_var.get(),
                    "start_date": self.start_date_var.get(),
                    "end_date": self.end_date_var.get(),
                    "strategy_type": self.strategy_var.get()
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                self.display_results(result)
                self.status_var.set("Backtest completed successfully")
            else:
                self.results_text.insert(tk.END, f"Error: {response.status_code}\n")
                self.status_var.set("Backtest failed")
                
        except Exception as e:
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
            self.status_var.set("Connection error")
    
    def display_results(self, result):
        """Display backtest results"""
        if "report" in result:
            report = result["report"]
            
            self.results_text.insert(tk.END, "\n📊 BACKTEST RESULTS\n")
            self.results_text.insert(tk.END, "-"*40 + "\n")
            
            # Performance
            perf = report.get("performance", {})
            self.results_text.insert(tk.END, "\n💰 Performance:\n")
            self.results_text.insert(tk.END, f"  Total Return: {perf.get('total_return', 'N/A')}\n")
            self.results_text.insert(tk.END, f"  Sharpe Ratio: {perf.get('sharpe_ratio', 'N/A')}\n")
            self.results_text.insert(tk.END, f"  Max Drawdown: {perf.get('max_drawdown', 'N/A')}\n")
            
            # Trading
            trade = report.get("trading", {})
            self.results_text.insert(tk.END, "\n📈 Trading:\n")
            self.results_text.insert(tk.END, f"  Total Trades: {trade.get('total_trades', 'N/A')}\n")
            self.results_text.insert(tk.END, f"  Win Rate: {trade.get('win_rate', 'N/A')}\n")
            self.results_text.insert(tk.END, f"  Profit Factor: {trade.get('profit_factor', 'N/A')}\n")
            
            # Prediction
            pred = report.get("prediction", {})
            self.results_text.insert(tk.END, "\n🎯 Prediction:\n")
            self.results_text.insert(tk.END, f"  Accuracy: {pred.get('accuracy', 'N/A')}\n")
            self.results_text.insert(tk.END, f"  R-Squared: {pred.get('r_squared', 'N/A')}\n")
            
            # Risk
            self.results_text.insert(tk.END, f"\n⚠️ Risk: {report.get('risk_assessment', 'N/A')}\n")
        
        self.results_text.see(tk.END)
    
    def train_models(self):
        """Train models for the symbol"""
        self.status_var.set("Training models...")
        self.results_text.insert(tk.END, f"\nTraining models for {self.symbol_var.get()}...\n")
        
        try:
            response = requests.post(
                f"{self.api_url}/api/train-models",
                json={
                    "symbols": [self.symbol_var.get()],
                    "training_days": 730
                }
            )
            
            if response.status_code == 200:
                self.results_text.insert(tk.END, "✅ Training initiated successfully\n")
                self.status_var.set("Training started")
            else:
                self.results_text.insert(tk.END, f"Training failed: {response.status_code}\n")
                self.status_var.set("Training failed")
                
        except Exception as e:
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
            self.status_var.set("Connection error")
    
    def clear_results(self):
        """Clear the results text"""
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = BacktestGUI(root)
    root.mainloop()
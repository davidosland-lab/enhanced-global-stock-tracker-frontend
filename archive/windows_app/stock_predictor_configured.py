#!/usr/bin/env python3
"""
Stock Predictor Pro - Configured Version
This version is pre-configured to connect to your cloud API
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
import sys
from datetime import datetime, timedelta
import queue

# Try to import optional packages
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: 'requests' not installed - will use local simulation")

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class StockPredictorConfigured:
    """Configured Stock Predictor Application with Cloud API Integration"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stock Predictor Pro - Cloud Connected")
        self.root.geometry("1200x700")
        
        # Load configuration
        self.config = self.load_config()
        
        # Set API endpoint from config
        self.cloud_api = self.config.get('api_settings', {}).get('cloud_api_url', 
                                   'https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev')
        
        # Data queue for async operations
        self.result_queue = queue.Queue()
        
        # Setup UI
        self.setup_ui()
        
        # Test cloud connection on startup
        self.root.after(1000, self.test_connection_silent)
        
    def load_config(self):
        """Load configuration from config.json"""
        config_file = "config.json"
        default_config = {
            "api_settings": {
                "cloud_api_url": "https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev",
                "timeout": 30
            },
            "endpoints": {
                "predict": "/api/predict",
                "predict_unified": "/api/predict_unified",
                "backtest": "/api/backtest",
                "health": "/health"
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    print(f"✓ Loaded config from {config_file}")
                    return config
        except Exception as e:
            print(f"Could not load config: {e}")
        
        return default_config
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Create main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="📈 Stock Predictor Pro - Cloud Connected", 
                         font=('Arial', 18, 'bold'))
        title.grid(row=0, column=0, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create tabs
        self.create_prediction_tab()
        self.create_backtest_tab()
        self.create_settings_tab()
        self.create_status_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Cloud API: " + self.cloud_api.split('-')[0] + "...")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def create_prediction_tab(self):
        """Create prediction tab"""
        pred_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(pred_frame, text="🎯 Predictions")
        
        # Input section
        input_frame = ttk.LabelFrame(pred_frame, text="Prediction Parameters", padding="10")
        input_frame.pack(fill="x", pady=5)
        
        # First row - Symbol and Timeframe
        row1 = ttk.Frame(input_frame)
        row1.pack(fill="x", pady=5)
        
        ttk.Label(row1, text="Symbol:").pack(side=tk.LEFT, padx=5)
        self.symbol_var = tk.StringVar(value="AAPL")
        self.symbol_entry = ttk.Entry(row1, textvariable=self.symbol_var, width=10)
        self.symbol_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Timeframe:").pack(side=tk.LEFT, padx=5)
        self.timeframe_var = tk.StringVar(value="1w")
        self.timeframe_combo = ttk.Combobox(row1, textvariable=self.timeframe_var,
                                           values=["1d", "1w", "1m", "3m", "1y"],
                                           width=10, state="readonly")
        self.timeframe_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Model:").pack(side=tk.LEFT, padx=5)
        self.model_var = tk.StringVar(value="ensemble")
        self.model_combo = ttk.Combobox(row1, textvariable=self.model_var,
                                       values=["ensemble", "lstm", "xgboost", "random_forest"],
                                       width=15, state="readonly")
        self.model_combo.pack(side=tk.LEFT, padx=5)
        
        # Processing mode
        self.mode_var = tk.StringVar(value="cloud")
        ttk.Radiobutton(row1, text="Cloud API", variable=self.mode_var, 
                       value="cloud").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(row1, text="Local Sim", variable=self.mode_var, 
                       value="local").pack(side=tk.LEFT, padx=5)
        
        # Predict button
        self.predict_btn = ttk.Button(row1, text="Generate Prediction",
                                    command=self.generate_prediction)
        self.predict_btn.pack(side=tk.LEFT, padx=20)
        
        # Results section
        results_frame = ttk.LabelFrame(pred_frame, text="Prediction Results", padding="10")
        results_frame.pack(fill="both", expand=True, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=20)
        self.results_text.pack(fill="both", expand=True)
        
    def create_backtest_tab(self):
        """Create backtesting tab"""
        backtest_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(backtest_frame, text="📊 Backtesting")
        
        # Backtest configuration
        config_frame = ttk.LabelFrame(backtest_frame, text="Backtest Configuration", padding="10")
        config_frame.pack(fill="x", pady=5)
        
        # Symbol and date range
        row1 = ttk.Frame(config_frame)
        row1.pack(fill="x", pady=5)
        
        ttk.Label(row1, text="Symbol:").pack(side=tk.LEFT, padx=5)
        self.bt_symbol_var = tk.StringVar(value="AAPL")
        ttk.Entry(row1, textvariable=self.bt_symbol_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Start Date:").pack(side=tk.LEFT, padx=5)
        self.bt_start_var = tk.StringVar(value="2023-01-01")
        ttk.Entry(row1, textvariable=self.bt_start_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="End Date:").pack(side=tk.LEFT, padx=5)
        self.bt_end_var = tk.StringVar(value="2024-01-01")
        ttk.Entry(row1, textvariable=self.bt_end_var, width=12).pack(side=tk.LEFT, padx=5)
        
        # Strategy and capital
        row2 = ttk.Frame(config_frame)
        row2.pack(fill="x", pady=5)
        
        ttk.Label(row2, text="Strategy:").pack(side=tk.LEFT, padx=5)
        self.bt_strategy_var = tk.StringVar(value="long_only")
        ttk.Combobox(row2, textvariable=self.bt_strategy_var,
                    values=["long_only", "long_short", "mean_reversion", "momentum"],
                    width=15, state="readonly").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Initial Capital:").pack(side=tk.LEFT, padx=5)
        self.bt_capital_var = tk.StringVar(value="100000")
        ttk.Entry(row2, textvariable=self.bt_capital_var, width=12).pack(side=tk.LEFT, padx=5)
        
        # Run backtest button
        self.backtest_btn = ttk.Button(row2, text="Run Backtest",
                                      command=self.run_backtest)
        self.backtest_btn.pack(side=tk.LEFT, padx=20)
        
        # Backtest mode
        self.bt_mode_var = tk.StringVar(value="cloud")
        ttk.Radiobutton(row2, text="Cloud", variable=self.bt_mode_var, 
                       value="cloud").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(row2, text="Local Sim", variable=self.bt_mode_var, 
                       value="local").pack(side=tk.LEFT, padx=5)
        
        # Results
        bt_results_frame = ttk.LabelFrame(backtest_frame, text="Backtest Results", padding="10")
        bt_results_frame.pack(fill="both", expand=True, pady=5)
        
        self.backtest_text = scrolledtext.ScrolledText(bt_results_frame, wrap=tk.WORD, height=15)
        self.backtest_text.pack(fill="both", expand=True)
        
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # API Settings
        api_frame = ttk.LabelFrame(settings_frame, text="API Configuration", padding="10")
        api_frame.pack(fill="x", pady=5)
        
        row1 = ttk.Frame(api_frame)
        row1.pack(fill="x", pady=5)
        
        ttk.Label(row1, text="Cloud API URL:").pack(side=tk.LEFT, padx=5)
        self.api_var = tk.StringVar(value=self.cloud_api)
        self.api_entry = ttk.Entry(row1, textvariable=self.api_var, width=60)
        self.api_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row1, text="Test Connection", 
                  command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1, text="Save Config", 
                  command=self.save_config).pack(side=tk.LEFT, padx=5)
        
        # Connection status
        self.conn_frame = ttk.LabelFrame(settings_frame, text="Connection Status", padding="10")
        self.conn_frame.pack(fill="x", pady=5)
        
        self.conn_status_text = tk.Text(self.conn_frame, height=10, width=80)
        self.conn_status_text.pack(fill="x")
        
    def create_status_tab(self):
        """Create status/info tab"""
        status_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(status_frame, text="ℹ️ Status")
        
        info_text = f"""
Stock Predictor Pro - Cloud Connected Version
=============================================

System Information:
• Python Version: {sys.version.split()[0]}
• Requests Library: {'✅ Installed' if HAS_REQUESTS else '❌ Not installed (using simulation)'}
• NumPy Library: {'✅ Installed' if HAS_NUMPY else '❌ Not installed'}

Cloud API Configuration:
• Endpoint: {self.cloud_api}
• Status: Will test on demand

Available Features:
✅ Cloud Predictions (with API)
✅ Local Simulation (no API needed)
✅ Backtesting (cloud or local)
✅ Multiple ML Models
✅ Technical Indicators

Endpoints Available:
• /api/predict - Single prediction
• /api/predict_unified - Unified predictions
• /api/backtest - Backtesting
• /health - API health check

© 2024 Stock Predictor Team
        """
        
        info_label = tk.Text(status_frame, height=25, width=80)
        info_label.insert(1.0, info_text)
        info_label.config(state='disabled')
        info_label.pack()
        
    def generate_prediction(self):
        """Generate stock prediction"""
        symbol = self.symbol_var.get()
        timeframe = self.timeframe_var.get()
        model = self.model_var.get()
        mode = self.mode_var.get()
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Generating prediction for {symbol}...\n\n")
        self.update_status(f"Processing {symbol}...")
        
        if mode == "cloud" and HAS_REQUESTS:
            # Use cloud API
            thread = threading.Thread(target=self.cloud_prediction,
                                    args=(symbol, timeframe, model))
            thread.daemon = True
            thread.start()
        else:
            # Use local simulation
            self.local_simulation_prediction(symbol, timeframe, model)
            
    def cloud_prediction(self, symbol, timeframe, model):
        """Get prediction from cloud API"""
        try:
            import requests
            
            # Try unified prediction endpoint first
            url = f"{self.cloud_api}/api/predict_unified"
            payload = {
                "symbol": symbol,
                "timeframe": timeframe,
                "model_type": model
            }
            
            self.update_status(f"Connecting to cloud API...")
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                self.display_cloud_results(result)
            else:
                # Try alternative endpoint
                url = f"{self.cloud_api}/api/predict"
                response = requests.post(url, json=payload, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    self.display_cloud_results(result)
                else:
                    raise Exception(f"API returned status {response.status_code}")
                    
        except Exception as e:
            error_msg = f"\n❌ Cloud API Error: {str(e)}\n\nFalling back to local simulation...\n"
            self.results_text.insert(tk.END, error_msg)
            self.local_simulation_prediction(symbol, timeframe, model)
            
    def display_cloud_results(self, result):
        """Display results from cloud API"""
        output = f"""
☁️ CLOUD PREDICTION RESULTS
{'='*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Symbol: {result.get('symbol', 'N/A')}
Current Price: ${result.get('current_price', 0):.2f}
Predicted Price: ${result.get('predicted_price', 0):.2f}
Change: {result.get('predicted_change', 0):.2f}%
Confidence: {result.get('confidence', 0):.1%}

Technical Indicators:
• RSI: {result.get('rsi', 'N/A')}
• MACD: {result.get('macd_signal', 'N/A')}
• Moving Averages: {result.get('ma_signal', 'N/A')}

Recommendation: {result.get('recommendation', 'N/A')}
Risk Level: {result.get('risk_level', 'N/A')}

{'='*60}
Source: Cloud API - {self.cloud_api.split('-')[0]}...
"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, output)
        self.update_status("Cloud prediction complete")
        
    def local_simulation_prediction(self, symbol, timeframe, model):
        """Generate local simulated prediction"""
        import random
        
        # Simulate processing delay
        self.root.after(500, lambda: self._show_local_prediction(symbol, timeframe, model))
        
    def _show_local_prediction(self, symbol, timeframe, model):
        """Show local simulation results"""
        import random
        
        current = round(random.uniform(100, 200), 2)
        change = round(random.uniform(-5, 5), 2)
        predicted = round(current * (1 + change/100), 2)
        confidence = round(random.uniform(0.6, 0.9), 2)
        
        output = f"""
🖥️ LOCAL SIMULATION RESULTS
{'='*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Symbol: {symbol}
Timeframe: {timeframe}
Model: {model}

Current Price: ${current}
Predicted Price: ${predicted}
Expected Change: {change:.2f}%
Confidence: {confidence:.1%}

Technical Indicators (Simulated):
• RSI: {random.randint(30, 70)}
• MACD: {'Bullish' if change > 0 else 'Bearish'}
• MA(50): ${round(current * 0.98, 2)}
• MA(200): ${round(current * 0.95, 2)}

Recommendation: {'BUY' if change > 1 else 'SELL' if change < -1 else 'HOLD'}
Risk Level: {'Low' if abs(change) < 2 else 'Medium' if abs(change) < 4 else 'High'}

{'='*60}
Note: This is a LOCAL SIMULATION for demonstration.
To get real predictions, connect to the cloud API.
{'='*60}
"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, output)
        self.update_status("Local simulation complete")
        
    def run_backtest(self):
        """Run backtesting"""
        symbol = self.bt_symbol_var.get()
        start_date = self.bt_start_var.get()
        end_date = self.bt_end_var.get()
        strategy = self.bt_strategy_var.get()
        capital = float(self.bt_capital_var.get())
        mode = self.bt_mode_var.get()
        
        self.backtest_text.delete(1.0, tk.END)
        self.backtest_text.insert(tk.END, f"Running backtest for {symbol}...\n\n")
        
        if mode == "cloud" and HAS_REQUESTS:
            # Cloud backtest
            thread = threading.Thread(target=self.cloud_backtest,
                                    args=(symbol, start_date, end_date, strategy, capital))
            thread.daemon = True
            thread.start()
        else:
            # Local simulation backtest
            self.local_simulation_backtest(symbol, start_date, end_date, strategy, capital)
            
    def cloud_backtest(self, symbol, start_date, end_date, strategy, capital):
        """Run backtest on cloud"""
        try:
            import requests
            
            url = f"{self.cloud_api}/api/backtest"
            payload = {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "strategy_type": strategy,
                "initial_capital": capital
            }
            
            self.update_status("Running cloud backtest...")
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                self.display_backtest_results(result, "cloud")
            else:
                raise Exception(f"API returned status {response.status_code}")
                
        except Exception as e:
            error_msg = f"\n❌ Cloud Backtest Error: {str(e)}\n\nUsing local simulation...\n"
            self.backtest_text.insert(tk.END, error_msg)
            self.local_simulation_backtest(symbol, start_date, end_date, strategy, capital)
            
    def local_simulation_backtest(self, symbol, start_date, end_date, strategy, capital):
        """Generate simulated backtest results"""
        import random
        
        # Simulate backtest
        total_return = round(random.uniform(-20, 50), 2)
        sharpe = round(random.uniform(0.5, 2.5), 2)
        max_dd = round(random.uniform(-25, -5), 2)
        win_rate = round(random.uniform(0.4, 0.7), 2)
        num_trades = random.randint(20, 200)
        
        output = f"""
🖥️ LOCAL BACKTEST SIMULATION
{'='*60}
Symbol: {symbol}
Period: {start_date} to {end_date}
Strategy: {strategy}
Initial Capital: ${capital:,.2f}

PERFORMANCE METRICS:
--------------------
Total Return: {total_return:.2f}%
Final Capital: ${capital * (1 + total_return/100):,.2f}
Sharpe Ratio: {sharpe}
Max Drawdown: {max_dd:.2f}%
Win Rate: {win_rate:.1%}
Total Trades: {num_trades}

TRADE STATISTICS:
-----------------
Avg Win: {random.uniform(1, 5):.2f}%
Avg Loss: {random.uniform(-5, -1):.2f}%
Best Trade: {random.uniform(5, 15):.2f}%
Worst Trade: {random.uniform(-15, -5):.2f}%
Avg Days in Position: {random.randint(5, 30)}

RISK METRICS:
-------------
Value at Risk (95%): {random.uniform(-5, -2):.2f}%
Expected Shortfall: {random.uniform(-8, -3):.2f}%
Calmar Ratio: {abs(total_return/max_dd):.2f}

{'='*60}
Note: This is a LOCAL SIMULATION.
For real backtesting with historical data,
connect to the cloud API.
{'='*60}
"""
        self.backtest_text.delete(1.0, tk.END)
        self.backtest_text.insert(1.0, output)
        self.update_status("Local backtest complete")
        
    def display_backtest_results(self, result, source):
        """Display backtest results"""
        output = f"""
☁️ CLOUD BACKTEST RESULTS
{'='*60}
{json.dumps(result, indent=2)}
{'='*60}
Source: Cloud API
"""
        self.backtest_text.delete(1.0, tk.END)
        self.backtest_text.insert(1.0, output)
        self.update_status("Cloud backtest complete")
        
    def test_connection(self):
        """Test cloud API connection"""
        if not HAS_REQUESTS:
            self.conn_status_text.delete(1.0, tk.END)
            self.conn_status_text.insert(1.0, "❌ 'requests' library not installed\n")
            self.conn_status_text.insert(tk.END, "Install with: pip install requests\n")
            return
            
        try:
            import requests
            
            self.conn_status_text.delete(1.0, tk.END)
            self.conn_status_text.insert(1.0, f"Testing connection to:\n{self.cloud_api}\n\n")
            
            # Test health endpoint
            response = requests.get(f"{self.cloud_api}/health", timeout=10)
            
            if response.status_code == 200:
                self.conn_status_text.insert(tk.END, "✅ Connection successful!\n\n")
                self.conn_status_text.insert(tk.END, f"Response: {response.text}\n")
                messagebox.showinfo("Success", "Cloud API connection successful!")
            else:
                self.conn_status_text.insert(tk.END, f"⚠️ API returned status {response.status_code}\n")
                
        except Exception as e:
            self.conn_status_text.insert(tk.END, f"❌ Connection failed:\n{str(e)}\n")
            messagebox.showerror("Connection Error", f"Failed to connect:\n{str(e)}")
            
    def test_connection_silent(self):
        """Test connection silently on startup"""
        if HAS_REQUESTS:
            try:
                import requests
                response = requests.get(f"{self.cloud_api}/health", timeout=5)
                if response.status_code == 200:
                    self.update_status(f"✅ Connected to cloud API")
                else:
                    self.update_status(f"⚠️ Cloud API unavailable - using local mode")
            except:
                self.update_status(f"📍 Local mode (cloud optional)")
                
    def save_config(self):
        """Save current configuration"""
        self.config['api_settings']['cloud_api_url'] = self.api_var.get()
        
        try:
            with open("config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
            messagebox.showinfo("Success", "Configuration saved!")
            self.cloud_api = self.api_var.get()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save config: {str(e)}")
            
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(f"{message} | {datetime.now().strftime('%H:%M:%S')}")
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("=" * 60)
    print("Stock Predictor Pro - Cloud Connected Version")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    # Check for config file
    if os.path.exists("config.json"):
        print("✓ Configuration file found")
    else:
        print("⚠ No config file - using defaults")
    
    # Check dependencies
    if HAS_REQUESTS:
        print("✓ Requests library available - Cloud API enabled")
    else:
        print("⚠ Requests library not installed - Local simulation only")
        print("  Install with: pip install requests")
    
    print()
    print("Starting application...")
    print("=" * 60)
    
    try:
        app = StockPredictorConfigured()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Startup Error", f"Failed to start:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
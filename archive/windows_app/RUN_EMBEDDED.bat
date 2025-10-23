@echo off
REM This batch file contains the Python code embedded
REM It creates the Python file if it doesn't exist, then runs it

echo ==========================================
echo Stock Predictor Pro - Embedded Launcher
echo ==========================================
echo.

REM Create the Python file if it doesn't exist
if not exist "stock_predictor_embedded.py" (
    echo Creating application file...
    (
        echo import tkinter as tk
        echo from tkinter import ttk, messagebox
        echo import random
        echo from datetime import datetime
        echo.
        echo root = tk.Tk(^)
        echo root.title("Stock Predictor Pro - Embedded"^)
        echo root.geometry("600x400"^)
        echo.
        echo frame = ttk.Frame(root, padding="10"^)
        echo frame.pack(fill=tk.BOTH, expand=True^)
        echo.
        echo ttk.Label(frame, text="Stock Predictor Pro", font=('Arial', 16, 'bold'^)^).pack(pady=10^)
        echo.
        echo input_frame = ttk.Frame(frame^)
        echo input_frame.pack(pady=10^)
        echo.
        echo ttk.Label(input_frame, text="Symbol:"^).pack(side=tk.LEFT^)
        echo symbol_var = tk.StringVar(value="AAPL"^)
        echo entry = ttk.Entry(input_frame, textvariable=symbol_var, width=10^)
        echo entry.pack(side=tk.LEFT, padx=5^)
        echo.
        echo result_text = tk.Text(frame, height=10, width=60^)
        echo result_text.pack(pady=10^)
        echo.
        echo def predict(^):
        echo     symbol = symbol_var.get(^)
        echo     price = round(random.uniform(100, 200^), 2^)
        echo     change = round(random.uniform(-5, 5^), 2^)
        echo     result = f"Symbol: {symbol}\nPrice: ${price}\nChange: {change}%%\n"
        echo     result += f"Recommendation: {'BUY' if change ^> 0 else 'SELL'}\n"
        echo     result += f"Time: {datetime.now(^).strftime('%%H:%%M:%%S'^)}"
        echo     result_text.delete(1.0, tk.END^)
        echo     result_text.insert(1.0, result^)
        echo.
        echo ttk.Button(input_frame, text="Predict", command=predict^).pack(side=tk.LEFT, padx=10^)
        echo.
        echo ttk.Label(frame, text="Minimal working version"^).pack(side=tk.BOTTOM^)
        echo.
        echo root.mainloop(^)
    ) > stock_predictor_embedded.py
    echo File created!
)

echo.
echo Running Stock Predictor Pro...
echo.

REM Try different Python commands
python stock_predictor_embedded.py 2>nul
if %errorlevel% equ 0 goto :Success

py stock_predictor_embedded.py 2>nul
if %errorlevel% equ 0 goto :Success

python3 stock_predictor_embedded.py 2>nul
if %errorlevel% equ 0 goto :Success

REM Try specific paths
"C:\Python39\python.exe" stock_predictor_embedded.py 2>nul
if %errorlevel% equ 0 goto :Success

"%LOCALAPPDATA%\Programs\Python\Python39\python.exe" stock_predictor_embedded.py 2>nul
if %errorlevel% equ 0 goto :Success

"C:\Users\david\AppData\Local\Microsoft\WindowsApps\python.exe" stock_predictor_embedded.py 2>nul
if %errorlevel% equ 0 goto :Success

echo.
echo ==========================================
echo ERROR: Could not run Python
echo ==========================================
echo.
echo Please install Python from python.org
echo.
pause
exit /b 1

:Success
echo.
echo Application closed.
pause
#!/usr/bin/env python3
"""
Quick Setup Script for Complete Stock Tracker
Downloads essential market data for fast backtesting
"""

import asyncio
import sys
from datetime import datetime
from historical_data_manager import HistoricalDataManager

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Complete Stock Tracker - Quick Setup{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print()

def print_status(message, status="info"):
    if status == "success":
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} {message}")
    elif status == "warning":
        print(f"{Colors.WARNING}⚠{Colors.ENDC} {message}")
    elif status == "error":
        print(f"{Colors.FAIL}✗{Colors.ENDC} {message}")
    else:
        print(f"{Colors.OKCYAN}•{Colors.ENDC} {message}")

async def download_essential_data():
    """Download essential market data for the application"""
    
    print_header()
    print_status("Initializing Historical Data Manager...")
    
    try:
        manager = HistoricalDataManager("historical_data")
        print_status("Historical Data Manager initialized", "success")
        
        # Get current statistics
        stats = manager.get_data_statistics()
        if stats.get('total_price_records', 0) > 0:
            print_status(f"Found existing data: {stats['total_price_records']:,} records", "warning")
            response = input("\nDo you want to update the data? (y/n): ")
            if response.lower() != 'y':
                print_status("Setup cancelled", "warning")
                return
        
        # Essential symbols to download
        print()
        print_status("Preparing to download essential market data...")
        
        essential_symbols = {
            "Australian Stocks": ["CBA.AX", "BHP.AX", "CSL.AX", "WBC.AX", "ANZ.AX", "NAB.AX"],
            "Global Indices": ["^AORD", "^GSPC", "^FTSE", "^DJI", "^IXIC"],
            "Major US Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"]
        }
        
        print()
        print("Symbols to download:")
        for category, symbols in essential_symbols.items():
            print(f"  {Colors.BOLD}{category}:{Colors.ENDC} {', '.join(symbols)}")
        
        print()
        print("Download options:")
        print("  1. Quick (1 month, daily + hourly)")
        print("  2. Standard (6 months, multiple intervals)")
        print("  3. Comprehensive (2 years, all intervals)")
        print("  4. Custom")
        
        choice = input("\nSelect option (1-4): ")
        
        # Set parameters based on choice
        if choice == "1":
            period = "1mo"
            intervals = ["1d", "1h"]
            print_status("Quick download selected (fastest)", "info")
        elif choice == "2":
            period = "6mo"
            intervals = ["1d", "1h", "30m"]
            print_status("Standard download selected (recommended)", "info")
        elif choice == "3":
            period = "2y"
            intervals = ["1m", "5m", "15m", "30m", "1h", "1d"]
            print_status("Comprehensive download selected (may take 10-15 minutes)", "warning")
        elif choice == "4":
            period = input("Enter period (1mo, 3mo, 6mo, 1y, 2y): ")
            interval_input = input("Enter intervals (comma-separated, e.g., 1d,1h,30m): ")
            intervals = [i.strip() for i in interval_input.split(",")]
            print_status(f"Custom download: {period}, intervals: {intervals}", "info")
        else:
            print_status("Invalid option, using standard settings", "warning")
            period = "6mo"
            intervals = ["1d", "1h", "30m"]
        
        # Flatten all symbols
        all_symbols = []
        for symbols in essential_symbols.values():
            all_symbols.extend(symbols)
        
        print()
        print_status(f"Starting download of {len(all_symbols)} symbols...")
        print_status(f"Period: {period}, Intervals: {', '.join(intervals)}")
        print()
        
        # Download data
        start_time = datetime.now()
        results = await manager.download_historical_data(
            symbols=all_symbols,
            period=period,
            intervals=intervals
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print results
        print()
        print_status(f"Download completed in {duration:.1f} seconds", "success")
        print_status(f"Successfully downloaded: {len(results)} symbols", "success")
        
        # Get updated statistics
        stats = manager.get_data_statistics()
        print()
        print("Database Statistics:")
        print(f"  • Total records: {stats.get('total_price_records', 0):,}")
        print(f"  • Unique symbols: {stats.get('unique_symbols', 0)}")
        print(f"  • Database size: {stats.get('database_size_mb', 0):.2f} MB")
        
        # Test CBA.AX data
        print()
        print_status("Testing CBA.AX data retrieval...")
        cba_data = manager.get_historical_data("CBA.AX", interval="1d")
        if not cba_data.empty:
            latest_price = cba_data['close'].iloc[-1]
            print_status(f"CBA.AX latest price: ${latest_price:.2f}", "success")
        
        print()
        print(f"{Colors.OKGREEN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}✓ Setup Complete!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'='*60}{Colors.ENDC}")
        print()
        print("Next steps:")
        print("  1. Run 'python backend.py' to start the server")
        print("  2. Open http://localhost:8002 in your browser")
        print("  3. Enjoy fast backtesting with local data!")
        
    except Exception as e:
        print_status(f"Error during setup: {str(e)}", "error")
        print()
        print("Troubleshooting:")
        print("  1. Ensure you have internet connection")
        print("  2. Check that yfinance is installed: pip install yfinance")
        print("  3. Try running with admin privileges if permission errors occur")
        sys.exit(1)

async def main():
    """Main entry point"""
    try:
        await download_essential_data()
    except KeyboardInterrupt:
        print()
        print_status("Setup interrupted by user", "warning")
        sys.exit(0)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
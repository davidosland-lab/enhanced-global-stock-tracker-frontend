"""
Centralized Symbol Configuration Module
========================================

Provides centralized symbol management across the trading platform with support
for environment variables, command-line arguments, and reasonable defaults.

Author: Enhanced Global Stock Tracker
Date: December 25, 2024
Version: 1.0
"""

import os
from typing import List, Optional


class SymbolConfig:
    """
    Manages symbol configuration across the platform
    
    Features:
    - Environment variable support for flexible configuration
    - Fallback defaults for common US stocks
    - Uppercase normalization
    - Whitespace trimming
    - Support for international exchanges (e.g., CBA.AX for ASX)
    
    Environment Variables:
        DEFAULT_SYMBOLS: Default symbols for production trading
        TEST_SYMBOLS: Symbols used in integration tests
        BACKTEST_SYMBOLS: Symbols used in backtest validation
        DEMO_SYMBOLS: Symbols used in demo/example code
    
    Example Usage:
        # Set via environment before running:
        # Windows: set DEFAULT_SYMBOLS=CBA.AX,BHP.AX,RIO.AX
        # Linux/Mac: export DEFAULT_SYMBOLS="CBA.AX,BHP.AX,RIO.AX"
        
        from symbol_config import SymbolConfig
        
        symbols = SymbolConfig.get_default_symbols()
        # Returns: ['CBA.AX', 'BHP.AX', 'RIO.AX'] if env var set
        # Returns: ['AAPL', 'GOOGL', 'MSFT', 'NVDA'] if no env var
    """
    
    # Default symbol sets (used when no environment variables are set)
    DEFAULT_US_STOCKS = 'AAPL,GOOGL,MSFT,NVDA'
    DEFAULT_TEST_STOCKS = 'AAPL,GOOGL,MSFT,NVDA,TSLA'
    DEFAULT_BACKTEST_STOCKS = 'AAPL,GOOGL,MSFT,NVDA,AMD'
    DEFAULT_DEMO_STOCKS = 'AAPL,GOOGL,MSFT'
    
    @staticmethod
    def _parse_symbols(symbol_string: str) -> List[str]:
        """
        Parse comma-separated symbol string into list
        
        Args:
            symbol_string: Comma-separated symbols (e.g., "AAPL,GOOGL,MSFT")
            
        Returns:
            List of uppercase, trimmed symbols
        """
        return [s.strip().upper() for s in symbol_string.split(',') if s.strip()]
    
    @staticmethod
    def get_default_symbols() -> List[str]:
        """
        Get default trading symbols from environment or fallback defaults
        
        Returns:
            List of symbol strings
            
        Environment Variable:
            DEFAULT_SYMBOLS: Comma-separated list (e.g., "CBA.AX,BHP.AX")
            
        Default Fallback:
            ['AAPL', 'GOOGL', 'MSFT', 'NVDA']
        """
        env_symbols = os.getenv('DEFAULT_SYMBOLS', SymbolConfig.DEFAULT_US_STOCKS)
        return SymbolConfig._parse_symbols(env_symbols)
    
    @staticmethod
    def get_test_symbols() -> List[str]:
        """
        Get test symbols from environment or defaults
        
        Returns:
            List of symbol strings for testing
            
        Environment Variable:
            TEST_SYMBOLS: Comma-separated list
            
        Default Fallback:
            ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'TSLA']
        """
        env_symbols = os.getenv('TEST_SYMBOLS', SymbolConfig.DEFAULT_TEST_STOCKS)
        return SymbolConfig._parse_symbols(env_symbols)
    
    @staticmethod
    def get_backtest_symbols() -> List[str]:
        """
        Get backtest symbols from environment or defaults
        
        Returns:
            List of symbol strings for backtesting
            
        Environment Variable:
            BACKTEST_SYMBOLS: Comma-separated list
            
        Default Fallback:
            ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'AMD']
        """
        env_symbols = os.getenv('BACKTEST_SYMBOLS', SymbolConfig.DEFAULT_BACKTEST_STOCKS)
        return SymbolConfig._parse_symbols(env_symbols)
    
    @staticmethod
    def get_demo_symbols() -> List[str]:
        """
        Get demo/example symbols from environment or defaults
        
        Returns:
            List of symbol strings for demos
            
        Environment Variable:
            DEMO_SYMBOLS: Comma-separated list
            
        Default Fallback:
            ['AAPL', 'GOOGL', 'MSFT']
        """
        env_symbols = os.getenv('DEMO_SYMBOLS', SymbolConfig.DEFAULT_DEMO_STOCKS)
        return SymbolConfig._parse_symbols(env_symbols)
    
    @staticmethod
    def get_symbols_from_env_or_default(
        env_var_name: str,
        default: str
    ) -> List[str]:
        """
        Generic method to get symbols from environment variable or default
        
        Args:
            env_var_name: Name of environment variable to check
            default: Default comma-separated symbol string
            
        Returns:
            List of parsed symbols
        """
        env_symbols = os.getenv(env_var_name, default)
        return SymbolConfig._parse_symbols(env_symbols)
    
    @staticmethod
    def validate_symbols(symbols: List[str]) -> bool:
        """
        Validate symbol list format
        
        Args:
            symbols: List of symbol strings to validate
            
        Returns:
            True if valid, False otherwise
            
        Validation Rules:
            - List must not be empty
            - Each symbol must be 1-10 characters
            - Symbols can contain letters, dots (for exchanges), and dashes
        """
        if not symbols:
            return False
        
        import re
        symbol_pattern = re.compile(r'^[A-Z0-9.\-]{1,10}$')
        
        for symbol in symbols:
            if not symbol_pattern.match(symbol):
                return False
        
        return True


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("SYMBOL CONFIGURATION MODULE - TEST")
    print("=" * 80)
    
    print("\n1. Default Symbols:")
    print(f"   {SymbolConfig.get_default_symbols()}")
    
    print("\n2. Test Symbols:")
    print(f"   {SymbolConfig.get_test_symbols()}")
    
    print("\n3. Backtest Symbols:")
    print(f"   {SymbolConfig.get_backtest_symbols()}")
    
    print("\n4. Demo Symbols:")
    print(f"   {SymbolConfig.get_demo_symbols()}")
    
    print("\n5. Environment Variables (if set):")
    for env_var in ['DEFAULT_SYMBOLS', 'TEST_SYMBOLS', 'BACKTEST_SYMBOLS', 'DEMO_SYMBOLS']:
        value = os.getenv(env_var)
        print(f"   {env_var}: {value if value else '(not set)'}")
    
    print("\n6. Validation Tests:")
    test_cases = [
        (['AAPL', 'GOOGL'], True),
        (['CBA.AX', 'BHP.AX'], True),
        ([], False),
        (['VALID', 'TOOLONGSYMBOL'], False),
    ]
    
    for symbols, expected in test_cases:
        result = SymbolConfig.validate_symbols(symbols)
        status = "✓" if result == expected else "✗"
        print(f"   {status} {symbols}: {result}")
    
    print("\n" + "=" * 80)
    print("To set custom symbols, use environment variables:")
    print("  Windows: set DEFAULT_SYMBOLS=CBA.AX,BHP.AX,RIO.AX")
    print("  Linux/Mac: export DEFAULT_SYMBOLS=\"CBA.AX,BHP.AX,RIO.AX\"")
    print("=" * 80)

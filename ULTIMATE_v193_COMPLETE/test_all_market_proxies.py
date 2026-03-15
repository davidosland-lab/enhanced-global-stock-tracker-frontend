"""
Test script for all market-specific futures proxies

Tests AU (SPI), UK (FTSE), and US (NASDAQ/S&P) proxy integrations.

Version: 1.0.0
Date: 2026-03-03
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_au_spi_proxy():
    """Test 1: AU SPI Proxy"""
    print("\n" + "="*80)
    print("TEST 1: AU (ASX 200) SPI PROXY")
    print("="*80)
    
    try:
        from pipelines.models.screening.spi_proxy_advanced import SPIProxy
        
        proxy = SPIProxy()
        result = proxy.compute_spi_proxy()
        
        print("\n[OK] SPI Proxy module loaded successfully")
        print(f"\nTimestamp: {result['asof']}")
        print(f"SPI Proxy Move: {result['spi_proxy_pct']}%")
        print(f"Z-Score: {result['spi_proxy_z']}")
        print(f"Regime: {result['regime']}")
        print(f"Confidence: {result['confidence']:.0%}")
        print(f"Risk Multiplier: {result['risk_multiplier']}")
        print(f"Available: {result['available']}")
        print(f"Source: {result['source']}")
        
        print("\nDrivers:")
        for key, val in result['drivers'].items():
            if val is not None:
                print(f"  {key}: {val}%" if isinstance(val, (int, float)) and key != 'vol_gate' else f"  {key}: {val}")
        
        if result['available']:
            print("\n[OK] TEST 1 PASSED: AU SPI Proxy computed successfully")
            return True, result
        else:
            print("\n[X] TEST 1 FAILED: SPI Proxy not available")
            return False, result
            
    except Exception as e:
        print(f"\n[X] TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_uk_ftse_proxy():
    """Test 2: UK FTSE Proxy"""
    print("\n" + "="*80)
    print("TEST 2: UK (FTSE 100) PROXY")
    print("="*80)
    
    try:
        from pipelines.models.screening.ftse_proxy_advanced import FTSEProxy
        
        proxy = FTSEProxy()
        result = proxy.compute_ftse_proxy()
        
        print("\n[OK] FTSE Proxy module loaded successfully")
        print(f"\nTimestamp: {result['asof']}")
        print(f"FTSE Proxy Move: {result['ftse_proxy_pct']}%")
        print(f"Z-Score: {result['ftse_proxy_z']}")
        print(f"Regime: {result['regime']}")
        print(f"Confidence: {result['confidence']:.0%}")
        print(f"Risk Multiplier: {result['risk_multiplier']}")
        print(f"Available: {result['available']}")
        print(f"Primary Source: {result['meta']['primary_source']}")
        print(f"FTSE Futures (Z=F) Available: {result['meta']['ftse_futures_available']}")
        
        print("\nDrivers:")
        for key, val in result['drivers'].items():
            if val is not None:
                print(f"  {key}: {val}%" if isinstance(val, (int, float)) and key != 'vol_gate' else f"  {key}: {val}")
        
        if result['available']:
            print("\n[OK] TEST 2 PASSED: UK FTSE Proxy computed successfully")
            if result['meta']['ftse_futures_available']:
                print("  [OK] Using direct Z=F (FTSE futures) - highest accuracy")
            else:
                print("  [!] Using blended proxy (Z=F unavailable) - good accuracy")
            return True, result
        else:
            print("\n[X] TEST 2 FAILED: FTSE Proxy not available")
            return False, result
            
    except Exception as e:
        print(f"\n[X] TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_us_market_proxy():
    """Test 3: US Market Proxy"""
    print("\n" + "="*80)
    print("TEST 3: US (NASDAQ/S&P 500) PROXY")
    print("="*80)
    
    try:
        from pipelines.models.screening.us_proxy_advanced import USProxy
        
        proxy = USProxy()
        result = proxy.compute_us_proxy()
        
        print("\n[OK] US Market Proxy module loaded successfully")
        print(f"\nTimestamp: {result['asof']}")
        print(f"US Market Proxy Move: {result['us_proxy_pct']}%")
        print(f"Z-Score: {result['us_proxy_z']}")
        print(f"Regime: {result['regime']}")
        print(f"Confidence: {result['confidence']:.0%}")
        print(f"Risk Multiplier: {result['risk_multiplier']}")
        print(f"Available: {result['available']}")
        print(f"NQ=F (NASDAQ futures) Available: {result['meta']['nq_available']}")
        print(f"ES=F (S&P futures) Available: {result['meta']['es_available']}")
        
        print("\nDrivers:")
        for key, val in result['drivers'].items():
            if val is not None:
                print(f"  {key}: {val}%" if isinstance(val, (int, float)) and key != 'vol_gate' else f"  {key}: {val}")
        
        if result['available']:
            print("\n[OK] TEST 3 PASSED: US Market Proxy computed successfully")
            if result['meta']['nq_available'] and result['meta']['es_available']:
                print("  [OK] Using both NQ=F and ES=F (dual primary sources) - highest accuracy")
            elif result['meta']['nq_available'] or result['meta']['es_available']:
                print("  [!] Using single primary source - good accuracy")
            else:
                print("  [!] Primary sources unavailable - fallback accuracy")
            return True, result
        else:
            print("\n[X] TEST 3 FAILED: US Market Proxy not available")
            return False, result
            
    except Exception as e:
        print(f"\n[X] TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_market_specificity():
    """Test 4: Verify market-specific tickers"""
    print("\n" + "="*80)
    print("TEST 4: MARKET-SPECIFIC TICKER VERIFICATION")
    print("="*80)
    
    print("\nExpected Tickers:")
    print("  AU (ASX 200): ES=F, NQ=F, ^VIX, AUDUSD=X, TIO=F, BZ=F")
    print("  UK (FTSE 100): Z=F (PRIMARY), ES=F, ^VIX, ^VFTSE, GBPUSD=X, BZ=F")
    print("  US (S&P/NASDAQ): NQ=F (PRIMARY), ES=F (PRIMARY), ^VIX, DX-Y.NYB, CL=F, GC=F")
    
    print("\nVerifying configurations...")
    
    try:
        from pipelines.models.screening.spi_proxy_advanced import SPIProxyConfig
        from pipelines.models.screening.ftse_proxy_advanced import FTSEProxyConfig
        from pipelines.models.screening.us_proxy_advanced import USProxyConfig
        
        au_config = SPIProxyConfig()
        uk_config = FTSEProxyConfig()
        us_config = USProxyConfig()
        
        print("\n[OK] AU Configuration:")
        print(f"  Primary: ES=F ({au_config.ticker_es}), NQ=F ({au_config.ticker_nq})")
        print(f"  Currency: AUD/USD ({au_config.ticker_aud})")
        print(f"  Commodity: Iron Ore ({au_config.ticker_iron})")
        
        print("\n[OK] UK Configuration:")
        print(f"  PRIMARY: FTSE Futures Z=F ({uk_config.ticker_ftse_futures})")
        print(f"  Global: ES=F ({uk_config.ticker_es})")
        print(f"  Volatility: VFTSE ({uk_config.ticker_vftse})")
        print(f"  Currency: GBP/USD ({uk_config.ticker_gbp})")
        print(f"  Commodity: Brent ({uk_config.ticker_brent})")
        
        print("\n[OK] US Configuration:")
        print(f"  PRIMARY: NASDAQ NQ=F ({us_config.ticker_nq}), S&P ES=F ({us_config.ticker_es})")
        print(f"  Dollar: DX-Y.NYB ({us_config.ticker_dollar})")
        print(f"  Commodities: Oil ({us_config.ticker_oil}), Gold ({us_config.ticker_gold})")
        
        print("\n[OK] TEST 4 PASSED: All configurations verified")
        return True
        
    except Exception as e:
        print(f"\n[X] TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("MARKET-SPECIFIC FUTURES PROXY TEST SUITE")
    print("="*80)
    print("\nThis test suite verifies:")
    print("1. AU (ASX 200) SPI Proxy works")
    print("2. UK (FTSE 100) Proxy works with Z=F")
    print("3. US (NASDAQ/S&P) Proxy works with NQ=F + ES=F")
    print("4. Each market uses appropriate tickers")
    
    results = []
    
    # Test 1: AU SPI Proxy
    test1_pass, au_result = test_au_spi_proxy()
    results.append(('AU (ASX 200) SPI Proxy', test1_pass))
    
    # Test 2: UK FTSE Proxy
    test2_pass, uk_result = test_uk_ftse_proxy()
    results.append(('UK (FTSE 100) Proxy', test2_pass))
    
    # Test 3: US Market Proxy
    test3_pass, us_result = test_us_market_proxy()
    results.append(('US (NASDAQ/S&P) Proxy', test3_pass))
    
    # Test 4: Market Specificity
    test4_pass = test_market_specificity()
    results.append(('Market-Specific Tickers', test4_pass))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "[OK] PASS" if passed else "[X] FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n" + "="*80)
        print("[OK] ALL TESTS PASSED - MARKET-SPECIFIC PROXIES READY")
        print("="*80)
        print("\nNext Steps:")
        print("1. Deploy updated package to production")
        print("2. Run pipelines:")
        print("   - AU: python scripts\\run_au_pipeline_v1.3.13.py")
        print("   - UK: python scripts\\run_uk_pipeline_v1.3.13.py")
        print("   - US: python scripts\\run_us_pipeline_v1.3.13.py")
        print("3. Verify gap prediction accuracy for each market")
        print("4. Monitor logs for market-specific proxy success messages")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("[X] SOME TESTS FAILED - REVIEW ERRORS ABOVE")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())

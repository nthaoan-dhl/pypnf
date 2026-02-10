#!/usr/bin/env python3
"""
Test script for DNSE snapshot provider.

Usage:
    # Set environment variables first
    export DNSE_SNAPSHOT_URL="https://your-api.com/snapshot?symbol={symbol}"
    export DNSE_API_KEY="your_key"  # Optional
    
    # Run test
    python test_dnse_snapshot.py FPT
    
    # Or test with multiple symbols
    python test_dnse_snapshot.py FPT VNM HPG
"""

import sys
import os
from dnse_provider import fetch_snapshot


def test_snapshot(symbol):
    """Test fetching snapshot for a symbol"""
    print(f"\n{'='*60}")
    print(f"Testing DNSE snapshot for: {symbol}")
    print(f"{'='*60}")
    
    try:
        data = fetch_snapshot(symbol)
        
        print(f"\n✅ Successfully fetched snapshot for {symbol}:")
        print(f"   Date:  {data['Date'][0]}")
        print(f"   Open:  {data['Open'][0]:,.2f}")
        print(f"   High:  {data['High'][0]:,.2f}")
        print(f"   Low:   {data['Low'][0]:,.2f}")
        print(f"   Close: {data['Close'][0]:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error fetching snapshot for {symbol}:")
        print(f"   {type(e).__name__}: {str(e)}")
        return False


def check_env_vars():
    """Check if required environment variables are set"""
    print("Checking environment variables...")
    print("-" * 60)
    
    snapshot_url = os.getenv('DNSE_SNAPSHOT_URL', '')
    base_url = os.getenv('DNSE_BASE_URL', '')
    endpoint = os.getenv('DNSE_SNAPSHOT_ENDPOINT', '')
    api_key = os.getenv('DNSE_API_KEY', '')
    
    if snapshot_url:
        print(f"✅ DNSE_SNAPSHOT_URL: {snapshot_url}")
    elif base_url and endpoint:
        print(f"✅ DNSE_BASE_URL: {base_url}")
        print(f"✅ DNSE_SNAPSHOT_ENDPOINT: {endpoint}")
    else:
        print("⚠️  No DNSE URL configured!")
        print("   Set DNSE_SNAPSHOT_URL or (DNSE_BASE_URL + DNSE_SNAPSHOT_ENDPOINT)")
        return False
    
    if api_key:
        print(f"✅ DNSE_API_KEY: {'*' * 8}{api_key[-4:]}")
    else:
        print("ℹ️  DNSE_API_KEY: Not set (optional)")
    
    print(f"ℹ️  DNSE_TIMEOUT: {os.getenv('DNSE_TIMEOUT', '10')} seconds")
    print(f"ℹ️  DNSE_SYMBOL_PARAM: {os.getenv('DNSE_SYMBOL_PARAM', 'symbol')}")
    
    return True


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("DNSE Snapshot Provider Test")
    print("=" * 60)
    
    # Check environment variables
    if not check_env_vars():
        print("\n❌ Environment not configured properly.")
        print("\nExample configuration:")
        print('  export DNSE_SNAPSHOT_URL="https://api.example.com/snapshot?symbol={symbol}"')
        print('  export DNSE_API_KEY="your_api_key_here"')
        sys.exit(1)
    
    # Get symbols from command line or use defaults
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
    else:
        print("\n⚠️  No symbols provided, using defaults: FPT, VNM")
        symbols = ['FPT', 'VNM']
    
    # Test each symbol
    results = {}
    for symbol in symbols:
        results[symbol] = test_snapshot(symbol.upper())
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for symbol, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {symbol}")
    
    print(f"\nTotal: {success_count}/{total_count} successful")
    
    if success_count == total_count:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()

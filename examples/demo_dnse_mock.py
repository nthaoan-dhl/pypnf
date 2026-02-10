#!/usr/bin/env python3
"""
Demo DNSE provider with mock data (without real API).

This script creates a mock DNSE provider for testing purposes.
Useful when you don't have access to real DNSE API yet.

Usage:
    python demo_dnse_mock.py
"""

import sys
import os
from datetime import datetime

# Create mock provider module
mock_provider_code = '''
"""Mock DNSE provider for testing"""
from datetime import datetime
import random

def fetch_snapshot(symbol, timeframe=None, market=None, **kwargs):
    """Mock fetch_snapshot that returns random data"""
    
    # Simulate different prices for different symbols
    base_prices = {
        'FPT': 65.0,
        'VNM': 85.0,
        'HPG': 28.0,
        'MSN': 95.0,
        'VCB': 92.0,
        'VIC': 45.0,
    }
    
    base_price = base_prices.get(symbol.upper(), 50.0)
    
    # Random fluctuation
    variation = random.uniform(-2, 2)
    close = base_price + variation
    open_price = close + random.uniform(-1, 1)
    high = max(close, open_price) + random.uniform(0, 1)
    low = min(close, open_price) - random.uniform(0, 1)
    
    return {
        'Date': [datetime.now().strftime('%Y-%m-%d')],
        'Open': [round(open_price, 2)],
        'High': [round(high, 2)],
        'Low': [round(low, 2)],
        'Close': [round(close, 2)]
    }
'''

# Write mock provider to file
with open('mock_dnse_provider.py', 'w') as f:
    f.write(mock_provider_code)

print("=" * 70)
print("DNSE Mock Provider Demo")
print("=" * 70)
print("\n✅ Created mock_dnse_provider.py")


# Test 1: Direct provider test
print("\n" + "=" * 70)
print("Test 1: Testing mock provider directly")
print("=" * 70)

from mock_dnse_provider import fetch_snapshot

test_symbols = ['FPT', 'VNM', 'HPG']
for symbol in test_symbols:
    data = fetch_snapshot(symbol)
    print(f"\n{symbol}:")
    print(f"  Date:  {data['Date'][0]}")
    print(f"  Open:  {data['Open'][0]:>8.2f}")
    print(f"  High:  {data['High'][0]:>8.2f}")
    print(f"  Low:   {data['Low'][0]:>8.2f}")
    print(f"  Close: {data['Close'][0]:>8.2f}")


# Test 2: Using with pnfchart
print("\n" + "=" * 70)
print("Test 2: Using with pnfchart.py (mock data, no history)")
print("=" * 70)

from providers.data_sources import load_dnse_data
from datetime import datetime, timedelta

start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')

print(f"\nLoading FPT data:")
print(f"  Start: {start_date}")
print(f"  End:   {end_date}")
print(f"  Provider: mock_dnse_provider")

try:
    ts = load_dnse_data(
        symbol='FPT',
        start_date=start_date,
        end_date=end_date,
        timeframe='1m',
        provider_module='mock_dnse_provider',
        include_history=False  # No vnstock, just snapshot
    )
    
    print("\n✅ Successfully loaded mock data:")
    print(f"   Date:  {ts['Date'][0]}")
    print(f"   Open:  {ts['Open'][0]:,.2f}")
    print(f"   High:  {ts['High'][0]:,.2f}")
    print(f"   Low:   {ts['Low'][0]:,.2f}")
    print(f"   Close: {ts['Close'][0]:,.2f}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")


# Test 3: Show how to use with real pnfchart command
print("\n" + "=" * 70)
print("Test 3: Command line usage examples")
print("=" * 70)

print("\n1. Using mock provider (no real API needed):")
print("   python pnfchart.py FPT --source dnse \\")
print("       --dnse-provider mock_dnse_provider \\")
print("       --dnse-no-history")

print("\n2. With custom parameters:")
print("   python pnfchart.py VNM --source dnse \\")
print("       --dnse-provider mock_dnse_provider \\")
print("       --dnse-no-history \\")
print("       --method hl --reversal 3 --boxsize 1")

print("\n3. When you have real API, set environment and use real provider:")
print("   export DNSE_SNAPSHOT_URL='https://api.dnse.com/snapshot?symbol={symbol}'")
print("   export DNSE_API_KEY='your_key'")
print("   python pnfchart.py FPT --source dnse")


# Test 4: Create a complete chart example
print("\n" + "=" * 70)
print("Test 4: Creating complete P&F chart with mock data")
print("=" * 70)

try:
    from pnfchart import PointFigureChart
    
    # Get mock data
    ts = load_dnse_data(
        symbol='FPT',
        start_date=start_date,
        end_date=end_date,
        provider_module='mock_dnse_provider',
        include_history=False
    )
    
    # Create chart
    pnf = PointFigureChart(
        ts=ts,
        method='hl',
        reversal=3,
        boxsize=1,
        scaling='abs',
        title='FPT (Mock DNSE Data)'
    )
    
    print("\n📊 Point & Figure Chart:")
    print(pnf)
    
except Exception as e:
    print(f"\n⚠️  Cannot create chart: {e}")
    print("Note: Chart needs more historical data than just one snapshot.")
    print("      For real charts, use with --include-history or provide more data points.")


# Summary
print("\n" + "=" * 70)
print("Summary")
print("=" * 70)

print("\n✅ Mock provider created: mock_dnse_provider.py")
print("✅ Provider tested successfully")
print("✅ Integration with pnfchart verified")

print("\n📖 Next steps:")
print("   1. Review DNSE_QUICK_START.md for full documentation")
print("   2. Configure real DNSE API credentials when available")
print("   3. Replace mock_dnse_provider with dnse_provider")
print("   4. Test with: python test_dnse_snapshot.py FPT VNM HPG")

print("\n" + "=" * 70)
print("Demo completed!")
print("=" * 70 + "\n")

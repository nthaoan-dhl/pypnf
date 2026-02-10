#!/usr/bin/env python3
"""Test cTrader API connection using the new HTTP-based provider"""

import sys
import os

# Load .env first before any imports
from dotenv import load_dotenv
load_dotenv('/workspaces/pypnf/.env')

sys.path.insert(0, '/workspaces/pypnf')

from ctrader_provider import fetch_ohlcv

print("=" * 60)
print("cTrader Open API - HTTP Connection Test")
print("=" * 60)

print("\n🔧 Configuration:")
print(f"   Host: {os.getenv('CTRADER_HOST')}")
print(f"   Port: {os.getenv('CTRADER_PORT')}")
print(f"   Account ID: {os.getenv('CTRADER_ACCOUNT_ID')}")
print(f"   Token: {os.getenv('CTRADER_ACCESS_TOKEN', 'NOT SET')[:30]}...")

print("\n🚀 Attempting to fetch EURUSD candles (2024-12-01 to 2024-12-07, hourly)...")

try:
    data = fetch_ohlcv('EURUSD', '2024-12-01', '2024-12-07', 'h1')
    
    print(f"\n✅ Success! Fetched {len(data['Date'])} candles")
    print(f"\n📊 Sample data (first 5 rows):")
    print(f"   Date                | Open      | High      | Low       | Close")
    print(f"   " + "-" * 60)
    
    for i in range(min(5, len(data['Date']))):
        print(f"   {data['Date'][i]} | {data['Open'][i]:.5f} | {data['High'][i]:.5f} | {data['Low'][i]:.5f} | {data['Close'][i]:.5f}")
    
    if len(data['Date']) > 5:
        print(f"   ... ({len(data['Date']) - 5} more rows)")
    
    print(f"\n✨ cTrader HTTP provider is working!")

except PermissionError as e:
    print(f"\n❌ Permission denied: {e}")
    print("   Check your CTRADER_ACCESS_TOKEN in .env")

except ValueError as e:
    print(f"\n❌ Value error: {e}")
    print("   Symbol might not exist or couldn't be resolved")

except ConnectionError as e:
    print(f"\n❌ Connection error: {e}")
    print(f"   Cannot reach {os.getenv('CTRADER_HOST')}:{os.getenv('CTRADER_PORT')}")
    print("   Verify CTRADER_HOST and CTRADER_PORT in .env")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"   Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

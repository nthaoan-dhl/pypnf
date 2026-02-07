#!/usr/bin/env python3
"""
Helper script to fetch cTrader Account ID using OAuth credentials from .env
Connects to cTrader Open API via TCP socket and sends GetAccountsRequest
"""

import os
import json
import socket
import time
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

CTRADER_CLIENT_ID = os.getenv('CTRADER_CLIENT_ID')
CTRADER_CLIENT_SECRET = os.getenv('CTRADER_CLIENT_SECRET')
CTRADER_ACCESS_TOKEN = os.getenv('CTRADER_ACCESS_TOKEN')
CTRADER_HOST = os.getenv('CTRADER_HOST', 'live.ctraderapi.com')
CTRADER_PORT = int(os.getenv('CTRADER_PORT', 5035))

print(f"🔍 Fetching cTrader Account ID...")
print(f"   Host: {CTRADER_HOST}:{CTRADER_PORT}")
print(f"   Client ID: {CTRADER_CLIENT_ID[:20]}...")
print()

# cTrader Open API uses a simple text-based protocol
# We'll send a GetAccountsRequest and parse the response

try:
    # Connect to cTrader API
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((CTRADER_HOST, CTRADER_PORT))
    print("✅ Connected to cTrader API")
    
    # Send ProtoMessage for GetAccountsRequest
    # Format: clientId|accessToken|GetAccountsRequest|{}
    request = f"{CTRADER_CLIENT_ID}|{CTRADER_ACCESS_TOKEN}|GetAccountsRequest|{{}}"
    sock.sendall(request.encode() + b'\n')
    print("✅ Sent GetAccountsRequest")
    
    # Receive response with timeout
    sock.settimeout(5)
    response = b''
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        except socket.timeout:
            break
    
    sock.close()
    
    response_str = response.decode('utf-8', errors='ignore').strip()
    print(f"\n📨 Response received ({len(response_str)} bytes)")
    print(f"   Raw: {response_str[:200]}...")
    
    # Parse response - look for accountId in the response
    if 'accountId' in response_str:
        print("\n✨ Found Account IDs:")
        for line in response_str.split('\n'):
            if 'accountId' in line:
                print(f"   {line}")
    else:
        print("\n⚠️  Response received but couldn't parse Account ID")
        print(f"    Full response:\n    {response_str}")
        print("\n💡 Try these alternatives:")
        print("   1. Check cTrader Web App (Settings > Account > Account ID)")
        print("   2. Check cTrader Desktop (Tools > Options > Account)")
        print("   3. Use Account ID from: https://secure.ctrader.com/profile")

except ConnectionRefusedError:
    print(f"❌ Connection refused to {CTRADER_HOST}:{CTRADER_PORT}")
    print("\n💡 Troubleshooting:")
    print("   - Verify CTRADER_HOST and CTRADER_PORT in .env are correct")
    print("   - Check if cTrader API server is running")
    print("   - For demo account: use 'demo.ctraderapi.com:5035'")
    print("   - For live account: use 'live.ctraderapi.com:5035'")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 If API connection fails, get Account ID manually:")
    print("   1. Log in to cTrader Web App or Desktop")
    print("   2. Go to Settings > Account > Account ID")
    print("   3. Copy the numeric ID (e.g., 38867915)")
    print("   4. Update CTRADER_ACCOUNT_ID in .env")

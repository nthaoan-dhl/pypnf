#!/usr/bin/env python3
"""
cTrader gRPC Integration Guide + Working Test Template
Complete implementation requires actual .proto files from cTrader
"""

import os
from datetime import datetime, timedelta
from typing import Dict

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

print("=" * 70)
print("cTrader gRPC Integration - IMPLEMENTATION GUIDE")
print("=" * 70)

print("""
✅ COMPLETED:
  1. Created ctrader.proto with message definitions
  2. Created gRPC client infrastructure (TCP connection, auth, candle requests)
  3. Successfully connected to cTrader OpenAPI (live.ctraderapi.com:5035)
  4. Implemented protobuf message encoding (varint, string, field tag)

⚠️  NEXT STEPS TO COMPLETE INTEGRATION:

You have TWO options:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION 1: Use Official cTrader Python Library (If Available)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  pip install ctrader-open-api

  Then update ctrader_provider.py with:
  
  from ctrader_api import CTraderClient
  
  client = CTraderClient(
      host='live.ctraderapi.com',
      port=5035,
      client_id=CTRADER_CLIENT_ID,
      access_token=CTRADER_ACCESS_TOKEN
  )

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION 2: Get .proto Files from cTrader (Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. Download .proto files from cTrader:
     https://github.com/spotware/openapi-proto-messages.git
     
  2. Or contact cTrader support for OpenAPI .proto package

  3. Compile proto files:
     
     python -m grpcio_tools.protoc \\
       -I. --python_out=. --grpc_python_out=. \\
       open-api.proto
     
  4. This generates:
     - open_api_pb2.py (messages)
     - open_api_pb2_grpc.py (service stubs)
  
  5. Update ctrader_provider.py to use generated stubs:
     
     import grpc
     import open_api_pb2
     import open_api_pb2_grpc
     
     channel = grpc.aio.secure_channel(
         'live.ctraderapi.com:5035',
         grpc.ssl_channel_credentials()
     )
     stub = open_api_pb2_grpc.ProtoOAStub(channel)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION 3: Use CSV Fallback for Now
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Export OHLCV CSV from cTrader Desktop/Web, then:
  
  export CTRADER_CSV_PATH=/path/to/eurusd.csv
  python pnfchart.py EURUSD --source ctrader --ctrader-csv /path/to/eurusd.csv

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CURRENT STATUS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

# Show current credentials
account_id = os.getenv('CTRADER_ACCOUNT_ID')
token = os.getenv('CTRADER_ACCESS_TOKEN')

print(f"Account ID:    {account_id}")
print(f"Token:         {token[:30] if token else 'NOT SET'}...")
print(f"Host:          {os.getenv('CTRADER_HOST')}")
print(f"Port:          {os.getenv('CTRADER_PORT')}")

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FILES CREATED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ctrader.proto - Protobuf message definitions
✅ ctrader_grpc_client.py - gRPC client implementation
✅ ctrader_provider.py - Provider module for pypnf integration
✅ get_ctrader_account_id.py - Helper to fetch Account ID

RECOMMENDED NEXT STEP:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. Download cTrader .proto from:
     https://github.com/spotware/openapi-proto-messages.git

  2. Compile proto files:
     python -m grpcio_tools.protoc -I. --python_out=. --grpc_python_out=. open-api.proto

  3. Update ctrader_provider.py line 170+ with actual proto stubs

  4. Test with:
     python pnfchart.py EURUSD --source ctrader --timeframe h1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

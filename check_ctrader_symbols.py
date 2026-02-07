#!/usr/bin/env python3
"""
Query and display all available symbols from cTrader account
"""

import os
import sys
import threading
import time
from dotenv import load_dotenv

load_dotenv()

try:
    from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints
    from ctrader_open_api.messages.OpenApiMessages_pb2 import (
        ProtoOAApplicationAuthReq, ProtoOAApplicationAuthRes,
        ProtoOAAccountAuthReq, ProtoOAAccountAuthRes,
        ProtoOASymbolsListReq, ProtoOASymbolsListRes, ProtoOAErrorRes
    )
    from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import ProtoHeartbeatEvent
    from twisted.internet import reactor
except ImportError as e:
    print(f"Error: {e}")
    print("Please install: pip install ctrader-open-api")
    sys.exit(1)

# Get credentials
CTRADER_HOST_TYPE = os.getenv('CTRADER_HOST_TYPE', 'live')
CTRADER_CLIENT_ID = os.getenv('CTRADER_CLIENT_ID', '')
CTRADER_CLIENT_SECRET = os.getenv('CTRADER_CLIENT_SECRET', '')
CTRADER_ACCESS_TOKEN = os.getenv('CTRADER_ACCESS_TOKEN', '')
CTRADER_ACCOUNT_ID = int(os.getenv('CTRADER_ACCOUNT_ID', 0))

if not all([CTRADER_CLIENT_ID, CTRADER_CLIENT_SECRET, CTRADER_ACCESS_TOKEN, CTRADER_ACCOUNT_ID]):
    print("Missing credentials in .env file")
    sys.exit(1)

result_symbols = None
error_msg = None

def main():
    global result_symbols, error_msg
    
    def reactor_thread():
        reactor.run(installSignalHandlers=False)
    
    thread = threading.Thread(target=reactor_thread, daemon=True)
    thread.start()
    time.sleep(0.5)
    
    def on_connected(client):
        print(f"✅ Connected to cTrader {CTRADER_HOST_TYPE} API")
        request = ProtoOAApplicationAuthReq()
        request.clientId = CTRADER_CLIENT_ID
        request.clientSecret = CTRADER_CLIENT_SECRET
        deferred = client.send(request)
        deferred.addErrback(on_error)
    
    def on_message_received(client, message):
        global result_symbols
        
        if message.payloadType == ProtoHeartbeatEvent().payloadType:
            return
            
        if message.payloadType == ProtoOAApplicationAuthRes().payloadType:
            print("✅ Application authenticated")
            request = ProtoOAAccountAuthReq()
            request.ctidTraderAccountId = CTRADER_ACCOUNT_ID
            request.accessToken = CTRADER_ACCESS_TOKEN
            deferred = client.send(request)
            deferred.addErrback(on_error)
            
        elif message.payloadType == ProtoOAAccountAuthRes().payloadType:
            print(f"✅ Account {CTRADER_ACCOUNT_ID} authenticated")
            print("\n⏳ Fetching symbol list...")
            request = ProtoOASymbolsListReq()
            request.ctidTraderAccountId = CTRADER_ACCOUNT_ID
            request.includeArchivedSymbols = False
            deferred = client.send(request)
            deferred.addErrback(on_error)
            
        elif message.payloadType == ProtoOASymbolsListRes().payloadType:
            symbols = Protobuf.extract(message)
            result_symbols = symbols
            reactor.callFromThread(reactor.stop)
            
        elif message.payloadType == ProtoOAErrorRes().payloadType:
            error = Protobuf.extract(message)
            on_error(f"API Error: {error.get('errorCode')} - {error.get('description', 'Unknown')}")
    
    def on_error(failure):
        global error_msg
        error_msg = str(failure)
        reactor.callFromThread(reactor.stop)
    
    def on_disconnected(client, reason):
        global error_msg
        if not result_symbols and not error_msg:
            error_msg = f"Disconnected: {reason}"
    
    host = EndPoints.PROTOBUF_LIVE_HOST if CTRADER_HOST_TYPE.lower() == 'live' else EndPoints.PROTOBUF_DEMO_HOST
    client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)
    client.setConnectedCallback(on_connected)
    client.setDisconnectedCallback(on_disconnected)
    client.setMessageReceivedCallback(on_message_received)
    
    reactor.callFromThread(client.startService)
    
    thread.join(timeout=30)
    
    if error_msg:
        print(f"\n❌ Error: {error_msg}")
        sys.exit(1)
    
    if not result_symbols:
        print("\n❌ No symbols received")
        sys.exit(1)
    
    # Display symbols
    print(f"\n{'='*80}")
    print(f"AVAILABLE SYMBOLS IN ACCOUNT {CTRADER_ACCOUNT_ID}")
    print(f"{'='*80}\n")
    
    # Handle both dict and object formats
    if hasattr(result_symbols, 'symbol'):
        symbols = result_symbols.symbol
    else:
        symbols = result_symbols.get('symbol', [])
    
    print(f"Total symbols: {len(symbols)}\n")
    
    # Group by category
    forex_symbols = []
    metal_symbols = []
    crypto_symbols = []
    other_symbols = []
    
    for sym in symbols:
        # Handle both dict and object
        if hasattr(sym, 'symbolName'):
            name = sym.symbolName
            sid = sym.symbolId
        else:
            name = sym.get('symbolName', '')
            sid = sym.get('symbolId', '')
        
        if not name:
            continue
            
        name_upper = name.upper()
        entry = f"{name:20} | ID: {sid:6}"
        
        if 'XAU' in name_upper or 'XAG' in name_upper or 'GOLD' in name_upper or 'SILVER' in name_upper:
            metal_symbols.append(entry)
        elif 'BTC' in name_upper or 'ETH' in name_upper or 'CRYPTO' in name_upper:
            crypto_symbols.append(entry)
        elif 'USD' in name_upper or 'EUR' in name_upper or 'GBP' in name_upper or 'JPY' in name_upper:
            forex_symbols.append(entry)
        else:
            other_symbols.append(entry)
    
    if metal_symbols:
        print("🥇 METALS / PRECIOUS:")
        for s in sorted(metal_symbols):
            print(f"   {s}")
        print()
    
    if crypto_symbols:
        print("₿ CRYPTO:")
        for s in sorted(crypto_symbols):
            print(f"   {s}")
        print()
    
    if forex_symbols:
        print("💱 FOREX:")
        for s in sorted(forex_symbols)[:20]:  # Show first 20
            print(f"   {s}")
        if len(forex_symbols) > 20:
            print(f"   ... and {len(forex_symbols) - 20} more")
        print()
    
    if other_symbols:
        print("📊 OTHER:")
        for s in sorted(other_symbols)[:10]:  # Show first 10
            print(f"   {s}")
        if len(other_symbols) > 10:
            print(f"   ... and {len(other_symbols) - 10} more")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import os, sys, threading, time
from dotenv import load_dotenv
load_dotenv()

from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import ProtoHeartbeatEvent
from twisted.internet import reactor

CTRADER_HOST_TYPE = os.getenv('CTRADER_HOST_TYPE', 'live')
CTRADER_CLIENT_ID = os.getenv('CTRADER_CLIENT_ID')
CTRADER_CLIENT_SECRET = os.getenv('CTRADER_CLIENT_SECRET')
CTRADER_ACCESS_TOKEN = os.getenv('CTRADER_ACCESS_TOKEN')
CTRADER_ACCOUNT_ID = int(os.getenv('CTRADER_ACCOUNT_ID', 0))

SYMBOLS_TO_CHECK = {
    'XAUUSD': 41,
    'BTCUSD': 1148,
    'EURUSD': 1,
}

result_symbols = {}
error_msg = None

def main():
    global result_symbols, error_msg
    
    def reactor_thread():
        reactor.run(installSignalHandlers=False)
    
    thread = threading.Thread(target=reactor_thread, daemon=True)
    thread.start()
    time.sleep(0.5)
    
    def on_connected(client):
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
            request = ProtoOAAccountAuthReq()
            request.ctidTraderAccountId = CTRADER_ACCOUNT_ID
            request.accessToken = CTRADER_ACCESS_TOKEN
            deferred = client.send(request)
            deferred.addErrback(on_error)
            
        elif message.payloadType == ProtoOAAccountAuthRes().payloadType:
            # Query symbol details
            for sym_name, sym_id in SYMBOLS_TO_CHECK.items():
                request = ProtoOASymbolByIdReq()
                request.ctidTraderAccountId = CTRADER_ACCOUNT_ID
                request.symbolId.append(sym_id)
                deferred = client.send(request)
                deferred.addErrback(on_error)
            
        elif message.payloadType == ProtoOASymbolByIdRes().payloadType:
            symbol_res = Protobuf.extract(message)
            if hasattr(symbol_res, 'symbol') and len(symbol_res.symbol) > 0:
                sym = symbol_res.symbol[0]
                result_symbols[sym.symbolId] = {
                    'name': sym.symbolName,
                    'id': sym.symbolId,
                    'digits': sym.digits,
                    'pipPosition': getattr(sym, 'pipPosition', 'N/A'),
                    'lotSize': getattr(sym, 'lotSize', 'N/A'),
                    'stepVolume': getattr(sym, 'stepVolume', 'N/A'),
                }
                
                if len(result_symbols) >= len(SYMBOLS_TO_CHECK):
                    reactor.callFromThread(reactor.stop)
    
    def on_error(failure):
        global error_msg
        error_msg = str(failure)
        reactor.callFromThread(reactor.stop)
    
    def on_disconnected(client, reason):
        pass
    
    host = EndPoints.PROTOBUF_LIVE_HOST if CTRADER_HOST_TYPE.lower() == 'live' else EndPoints.PROTOBUF_DEMO_HOST
    client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)
    client.setConnectedCallback(on_connected)
    client.setDisconnectedCallback(on_disconnected)
    client.setMessageReceivedCallback(on_message_received)
    
    reactor.callFromThread(client.startService)
    
    thread.join(timeout=30)
    
    if error_msg:
        print(f"Error: {error_msg}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"SYMBOL DETAILS")
    print(f"{'='*70}\n")
    
    for sym_id, details in result_symbols.items():
        print(f"{details['name']:10} (ID: {sym_id:4})")
        print(f"  Digits: {details['digits']}")
        print(f"  PipPosition: {details['pipPosition']}")
        print(f"  LotSize: {details['lotSize']}")
        print(f"  StepVolume: {details['stepVolume']}")
        print()

if __name__ == '__main__':
    main()

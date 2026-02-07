#!/usr/bin/env python3
"""
cTrader OpenAPI Client - Using Official ctrader-open-api Library
Fetches live candlestick data via cTrader OpenAPI
Falls back to test data if credentials not available
"""

import os
import random
import calendar
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try importing the official ctrader-open-api library
CTRADER_API_AVAILABLE = False
try:
    from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints
    from ctrader_open_api.messages.OpenApiMessages_pb2 import (
        ProtoOAApplicationAuthReq, ProtoOAApplicationAuthRes,
        ProtoOAAccountAuthReq, ProtoOAAccountAuthRes,
        ProtoOAGetTrendbarsReq, ProtoOAGetTrendbarsRes,
        ProtoOASymbolByIdReq, ProtoOAErrorRes,
        ProtoOASubscribeSpotsRes
    )
    from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import ProtoHeartbeatEvent
    from ctrader_open_api.messages.OpenApiModelMessages_pb2 import ProtoOATrendbarPeriod
    from twisted.internet import reactor
    CTRADER_API_AVAILABLE = True
    print("✅ ctrader-open-api library available - Live mode enabled")
except ImportError as e:
    print(f"⚠️  ctrader-open-api not available: {e}")
    print("   Install: pip install ctrader-open-api")
    print("   Falling back to test data mode")

# Configuration
CTRADER_HOST_TYPE = os.getenv('CTRADER_HOST_TYPE', 'live')  # 'live' or 'demo'
CTRADER_CLIENT_ID = os.getenv('CTRADER_CLIENT_ID', '')
CTRADER_CLIENT_SECRET = os.getenv('CTRADER_CLIENT_SECRET', '')
CTRADER_ACCESS_TOKEN = os.getenv('CTRADER_ACCESS_TOKEN', '')
CTRADER_ACCOUNT_ID = os.getenv('CTRADER_ACCOUNT_ID', '')

# Parse account ID
if CTRADER_ACCOUNT_ID:
    try:
        CTRADER_ACCOUNT_ID = int(CTRADER_ACCOUNT_ID)
    except (ValueError, TypeError):
        CTRADER_ACCOUNT_ID = None

# Timeframe mapping to ProtoOATrendbarPeriod enum
TIMEFRAME_TO_PERIOD = {
    'm1': 'M1', '1m': 'M1',
    'm5': 'M5', '5m': 'M5',
    'm15': 'M15', '15m': 'M15',
    'm30': 'M30', '30m': 'M30',
    'h1': 'H1', '1h': 'H1',
    'h4': 'H4', '4h': 'H4',
    'd1': 'D1', '1d': 'D1',
    'w1': 'W1', '1w': 'W1',
}

# Symbol IDs (from account 24570842)
# Run check_ctrader_symbols.py to get correct IDs for your account
SYMBOL_ID_MAP = {
    # Forex pairs
    'EURUSD': 1, 'GBPUSD': 2, 'USDJPY': 3, 'USDCHF': 4, 
    'AUDUSD': 5, 'AUDJPY': 11, 'USDCAD': 6, 'NZDUSD': 7,
    'CADJPY': 15, 'CHFJPY': 13,
    
    # Metals (precious)
    'XAUUSD': 41,  # Gold
    'XAGUSD': 42,  # Silver  
    'XAUEUR': 1109,
    'XAGEUR': 1108,
    
    # Crypto
    'BTCUSD': 1148, 'BTCEUR': 1144, 'BTCGBP': 1145,
    'ETHUSD': 1162, 'ETHEUR': 1158,
    'BCHUSD': 1150,
    'BNBUSD': 2928, 'ADAUSD': 2930, 'DOGUSD': 2933,
    
    # Indices (examples)
    'SPX500': 18, 'US100': 19, 'US30': 20, 'USTEC': 21,
    'DXY': 12, 'BRENT': 10, 'WTI': 11,
}

# Test data price ranges
SYMBOL_PRICES = {
    'EURUSD': (0.95, 1.10), 'GBPUSD': (1.20, 1.35), 'USDJPY': (130, 155),
    'USDCHF': (0.85, 1.05), 'AUDUSD': (0.60, 0.75), 'USDCAD': (1.25, 1.40),
    'NZDUSD': (0.55, 0.70), 'XAUUSD': (1800, 2100), 'XAGUUSD': (20, 32),
}


def _generate_test_candles(symbol: str, start_date: str, end_date: str, 
                          timeframe: str) -> Dict:
    """Generate realistic OHLCV test data"""
    
    start_price, price_range = SYMBOL_PRICES.get(symbol.upper(), (1.0, 0.2))
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    tf_minutes = {
        'm1': 1, 'm5': 5, 'm15': 15, 'm30': 30,
        'h1': 60, 'h4': 240, 'd1': 1440, 'w1': 10080,
        '1m': 1, '5m': 5, '15m': 15, '30m': 30,
        '1h': 60, '4h': 240, '1d': 1440, '1w': 10080,
    }.get(timeframe.lower(), 60)
    
    dates, opens, highs, lows, closes = [], [], [], [], []
    
    current_dt = start_dt
    current_price = start_price + random.uniform(-price_range/2, price_range/2)
    
    while current_dt <= end_dt:
        # Skip weekends for FX
        if symbol.upper() not in ['BRENT', 'WTI'] and current_dt.weekday() >= 5:
            current_dt += timedelta(minutes=tf_minutes)
            continue
        
        open_price = current_price
        change = random.uniform(-0.005, 0.005) * open_price
        close_price = open_price + change
        
        high_price = max(open_price, close_price) + abs(random.uniform(0, 0.003) * open_price)
        low_price = min(open_price, close_price) - abs(random.uniform(0, 0.003) * open_price)
        
        dates.append(current_dt.strftime('%Y-%m-%d %H:%M:%S'))
        opens.append(round(open_price, 5))
        highs.append(round(high_price, 5))
        lows.append(round(low_price, 5))
        closes.append(round(close_price, 5))
        
        current_price = close_price
        current_dt += timedelta(minutes=tf_minutes)
    
    return {
        'Date': dates,
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes
    }


class CTraderApiWrapper:
    """Synchronous wrapper for async ctrader-open-api library"""
    
    # Shared state across instances to avoid reactor restart
    _reactor_started = False
    _reactor_thread = None
    
    def __init__(self, host_type: str, client_id: str, client_secret: str, 
                 access_token: str, account_id: int):
        self.host_type = host_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.account_id = account_id
        self.result = None
        self.error = None
        self.client = None
        self.authenticated = False
        self.symbol_digits = {}  # Cache symbol digits
        
    @classmethod
    def _ensure_reactor_running(cls):
        """Ensure reactor is running in background thread"""
        if not cls._reactor_started:
            def reactor_thread():
                reactor.run(installSignalHandlers=False)
            
            cls._reactor_thread = threading.Thread(target=reactor_thread, daemon=True)
            cls._reactor_thread.start()
            cls._reactor_started = True
            
            # Give reactor time to start
            import time
            time.sleep(0.5)
        
    def run(self, symbol: str, period_name: str, from_ts: int, to_ts: int) -> Dict:
        """Run the async client in a thread and wait for results"""
        
        def reactor_thread():
            # Run reactor in this thread
            reactor.run(installSignalHandlers=False)
        
        # Start reactor in background thread
        thread = threading.Thread(target=reactor_thread, daemon=True)
        thread.start()
        
        # Give reactor time to start
        import time
        time.sleep(0.5)
        
        # Set up client callbacks
        def on_connected(client):
            self.client = client
            request = ProtoOAApplicationAuthReq()
            request.clientId = self.client_id
            request.clientSecret = self.client_secret
            deferred = client.send(request)
            deferred.addErrback(on_error)
        
        def on_message_received(client, message):
            # Ignore heartbeat and subscription messages
            if message.payloadType in [ProtoHeartbeatEvent().payloadType, 
                                      ProtoOASubscribeSpotsRes().payloadType]:
                return
                
            if message.payloadType == ProtoOAApplicationAuthRes().payloadType:
                # Application authorized, now authorize account
                request = ProtoOAAccountAuthReq()
                request.ctidTraderAccountId = self.account_id
                request.accessToken = self.access_token
                deferred = client.send(request)
                deferred.addErrback(on_error)
                
            elif message.payloadType == ProtoOAAccountAuthRes().payloadType:
                # Account authorized, now get trendbars
                self.authenticated = True
                self._fetch_trendbars(client, symbol, period_name, from_ts, to_ts)
                
            elif message.payloadType == ProtoOAGetTrendbarsRes().payloadType:
                # Trendbars received
                trendbar_res = Protobuf.extract(message)
                self.result = trendbar_res
                reactor.callFromThread(reactor.stop)
                
            elif message.payloadType == ProtoOAErrorRes().payloadType:
                # Error received
                error_res = Protobuf.extract(message)
                self.error = f"API Error: {error_res.get('errorCode')} - {error_res.get('description', 'Unknown')}"
                reactor.callFromThread(reactor.stop)
        
        def on_error(failure):
            self.error = str(failure)
            reactor.callFromThread(reactor.stop)
        
        def on_disconnected(client, reason):
            if not self.result and not self.error:
                self.error = f"Disconnected: {reason}"
        
        # Set up client
        host = EndPoints.PROTOBUF_LIVE_HOST if self.host_type.lower() == 'live' else EndPoints.PROTOBUF_DEMO_HOST
        client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)
        client.setConnectedCallback(on_connected)
        client.setDisconnectedCallback(on_disconnected)
        client.setMessageReceivedCallback(on_message_received)
        
        # Start client from reactor thread
        reactor.callFromThread(client.startService)
        
        # Wait for completion (max 30 seconds)
        thread.join(timeout=30)
        
        if self.error:
            raise RuntimeError(self.error)
        
        return self.result
    
    def _fetch_trendbars(self, client, symbol: str, period_name: str, from_ts: int, to_ts: int):
        """Fetch trendbars after authentication"""
        # Get symbol ID
        symbol_key = symbol.replace('/', '').upper()
        symbol_id = SYMBOL_ID_MAP.get(symbol_key)
        
        if not symbol_id:
            # Need to query symbol list first
            req = ProtoOASymbolByIdReq()
            req.ctidTraderAccountId = self.account_id
            # For now, raise error if symbol not in map
            raise RuntimeError(f"Symbol {symbol} not found in SYMBOL_ID_MAP")
        
        request = ProtoOAGetTrendbarsReq()
        request.ctidTraderAccountId = self.account_id
        request.fromTimestamp = from_ts
        request.toTimestamp = to_ts
        request.period = ProtoOATrendbarPeriod.Value(period_name)
        request.symbolId = symbol_id
        
        deferred = client.send(request)
        deferred.addErrback(lambda f: setattr(self, 'error', str(f)))


def fetch_ohlcv(symbol: str, start_date: str, end_date: str, timeframe: str = 'h1') -> Dict:
    """
    Fetch OHLCV data from cTrader via official OpenAPI library.

    With credentials: Connects to live cTrader OpenAPI
    Without credentials: Generates realistic test data

    Args:
        symbol: Trading symbol (e.g., 'EURUSD', 'XAUUSD')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        timeframe: Timeframe (m1, h1, d1, etc.)

    Returns:
        Dict with keys: Date, Open, High, Low, Close
    """

    # Check if we have required credentials
    has_credentials = (
        CTRADER_CLIENT_ID and 
        CTRADER_CLIENT_SECRET and 
        CTRADER_ACCESS_TOKEN and 
        CTRADER_ACCOUNT_ID
    )
    
    if not has_credentials:
        print("⚠️  Missing cTrader credentials; using test data")
        print("   Required: CTRADER_CLIENT_ID, CTRADER_CLIENT_SECRET, CTRADER_ACCESS_TOKEN, CTRADER_ACCOUNT_ID")
        return _generate_test_candles(symbol, start_date, end_date, timeframe)

    if not CTRADER_API_AVAILABLE:
        print("⚠️  ctrader-open-api library not available; using test data")
        return _generate_test_candles(symbol, start_date, end_date, timeframe)

    # Map timeframe to period name
    period_name = TIMEFRAME_TO_PERIOD.get(timeframe.lower())
    if period_name is None:
        raise ValueError(f"Invalid timeframe: {timeframe}")

    # Convert dates to timestamps
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    end_dt = end_dt + timedelta(hours=23, minutes=59, seconds=59)

    from_ts = int(calendar.timegm(start_dt.utctimetuple())) * 1000
    to_ts = int(calendar.timegm(end_dt.utctimetuple())) * 1000

    print(f"🔗 Fetching {symbol} from cTrader OpenAPI ({CTRADER_HOST_TYPE})")

    try:
        # Use the wrapper to fetch data
        wrapper = CTraderApiWrapper(
            host_type=CTRADER_HOST_TYPE,
            client_id=CTRADER_CLIENT_ID,
            client_secret=CTRADER_CLIENT_SECRET,
            access_token=CTRADER_ACCESS_TOKEN,
            account_id=CTRADER_ACCOUNT_ID
        )
        
        trendbar_res = wrapper.run(symbol, period_name, from_ts, to_ts)
        
        # Parse trendbars
        dates, opens, highs, lows, closes = [], [], [], [], []
        
        if not trendbar_res:
            raise RuntimeError("No trendbar response")
            
        trendbars = trendbar_res.get('trendbar', []) if isinstance(trendbar_res, dict) else []
        if hasattr(trendbar_res, 'trendbar'):
            trendbars = trendbar_res.trendbar
        
        for bar in trendbars:
            # Get digits for this symbol (assume 5 for FX, 2 for gold/silver)
            is_metal = symbol.upper() in ['XAUUSD', 'XAGUSD', 'GOLD', 'SILVER']
            digits = 2 if is_metal else 5
            divisor = 10 ** digits
            
            # Handle both dict and object formats
            if isinstance(bar, dict):
                low = bar['low']
                open_p = low + bar.get('deltaOpen', 0)
                close_p = low + bar.get('deltaClose', 0)
                high_p = low + bar.get('deltaHigh', 0)
                timestamp_min = bar.get('utcTimestampInMinutes', 0)
            else:
                low = bar.low
                open_p = low + bar.deltaOpen
                close_p = low + bar.deltaClose
                high_p = low + bar.deltaHigh
                timestamp_min = bar.utcTimestampInMinutes

            dt = datetime.utcfromtimestamp(timestamp_min * 60)
            
            dates.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
            opens.append(round(open_p / divisor, digits))
            highs.append(round(high_p / divisor, digits))
            lows.append(round(low / divisor, digits))
            closes.append(round(close_p / divisor, digits))

        if not dates:
            raise RuntimeError("No trendbars returned")

        return {
            'Date': dates,
            'Open': opens,
            'High': highs,
            'Low': lows,
            'Close': closes,
        }

    except Exception as e:
        print(f"⚠️  Live data failed: {e}")
        print("📊 Using test data instead")
        return _generate_test_candles(symbol, start_date, end_date, timeframe)
        client.close()

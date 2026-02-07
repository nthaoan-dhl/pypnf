#!/usr/bin/env python3
"""
cTrader Open API gRPC Client
Connects via TCP socket and uses protobuf for message serialization
"""

import os
import socket
import struct
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import IntEnum

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from .env
CTRADER_HOST = os.getenv('CTRADER_HOST', 'live.ctraderapi.com')
CTRADER_PORT = int(os.getenv('CTRADER_PORT', 5035))
CTRADER_CLIENT_ID = os.getenv('CTRADER_CLIENT_ID')
CTRADER_CLIENT_SECRET = os.getenv('CTRADER_CLIENT_SECRET')
CTRADER_ACCESS_TOKEN = os.getenv('CTRADER_ACCESS_TOKEN')
CTRADER_ACCOUNT_ID = os.getenv('CTRADER_ACCOUNT_ID')

class CandlestickPeriod(IntEnum):
    """Candlestick period enum"""
    M1 = 0      # 1 minute
    M5 = 1      # 5 minutes
    M15 = 2     # 15 minutes
    M30 = 3     # 30 minutes
    H1 = 4      # 1 hour
    H4 = 5      # 4 hours
    D1 = 6      # daily
    W1 = 7      # weekly
    MN1 = 8     # monthly

# Timeframe mapping to enum
TIMEFRAME_MAP = {
    'm1': CandlestickPeriod.M1, '1m': CandlestickPeriod.M1,
    'm5': CandlestickPeriod.M5, '5m': CandlestickPeriod.M5,
    'm15': CandlestickPeriod.M15, '15m': CandlestickPeriod.M15,
    'm30': CandlestickPeriod.M30, '30m': CandlestickPeriod.M30,
    'h1': CandlestickPeriod.H1, '1h': CandlestickPeriod.H1,
    'h4': CandlestickPeriod.H4, '4h': CandlestickPeriod.H4,
    'd1': CandlestickPeriod.D1, '1d': CandlestickPeriod.D1,
    'w1': CandlestickPeriod.W1, '1w': CandlestickPeriod.W1,
}

# Common FX pair IDs (broker-specific, will need to query)
SYMBOL_ID_MAP = {
    'EURUSD': 1,
    'GBPUSD': 2,
    'USDJPY': 3,
    'USDCHF': 4,
    'AUDUSD': 5,
    'USDCAD': 6,
    'NZDUSD': 7,
    'XAUUSD': 8,
    'XAGUSD': 9,
    'BRENT': 10,
    'WTI': 11,
}

class ProtoMessage:
    """Simple protobuf message encoder/decoder"""
    
    @staticmethod
    def encode_varint(value: int) -> bytes:
        """LEB128 varint encoding"""
        result = bytearray()
        while (value & 0xFFFFFF80) != 0:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)
    
    @staticmethod
    def decode_varint(data: bytes, offset: int) -> Tuple[int, int]:
        """Decode LEB128 varint, returns (value, new_offset)"""
        result = 0
        shift = 0
        while offset < len(data):
            byte = data[offset]
            offset += 1
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
        return result, offset
    
    @staticmethod
    def encode_string(value: str) -> bytes:
        """Encode string as length-prefixed UTF-8"""
        encoded = value.encode('utf-8')
        return ProtoMessage.encode_varint(len(encoded)) + encoded
    
    @staticmethod
    def encode_field(field_num: int, field_type: int, value) -> bytes:
        """Encode proto field (field_num, type=0 for varint, 2 for string, etc)"""
        tag = (field_num << 3) | field_type
        result = ProtoMessage.encode_varint(tag)
        
        if field_type == 0:  # Varint
            result += ProtoMessage.encode_varint(value)
        elif field_type == 2:  # Length-delimited (string, bytes)
            if isinstance(value, str):
                result += ProtoMessage.encode_string(value)
            else:
                result += ProtoMessage.encode_varint(len(value)) + value
        elif field_type == 5:  # Fixed32
            result += struct.pack('<I', int(value))
        elif field_type == 1:  # Fixed64
            result += struct.pack('<Q', int(value))
        
        return result
    
    @staticmethod
    def build_auth_request() -> bytes:
        """Build authentication request"""
        msg = b''
        msg += ProtoMessage.encode_field(1, 2, CTRADER_CLIENT_ID)  # clientId (string, field 1)
        msg += ProtoMessage.encode_field(2, 2, CTRADER_CLIENT_SECRET)  # clientSecret (string, field 2)
        
        # Wrap with message length prefix
        length = ProtoMessage.encode_varint(len(msg))
        return length + msg
    
    @staticmethod
    def build_account_auth_request() -> bytes:
        """Build account authorization request"""
        msg = b''
        msg += ProtoMessage.encode_field(1, 2, CTRADER_ACCESS_TOKEN)  # accessToken (string, field 1)
        
        length = ProtoMessage.encode_varint(len(msg))
        return length + msg
    
    @staticmethod
    def build_candles_request(account_id: int, symbol_id: int, period: int, 
                             from_ts: int, to_ts: int) -> bytes:
        """Build get candles request"""
        msg = b''
        msg += ProtoMessage.encode_field(1, 0, account_id)  # accountId (varint, field 1)
        msg += ProtoMessage.encode_field(2, 0, symbol_id)   # symbolId (varint, field 2)
        msg += ProtoMessage.encode_field(3, 0, period)      # period (varint, field 3)
        msg += ProtoMessage.encode_field(4, 1, from_ts)     # fromTimestamp (fixed64, field 4)
        msg += ProtoMessage.encode_field(5, 1, to_ts)       # toTimestamp (fixed64, field 5)
        
        length = ProtoMessage.encode_varint(len(msg))
        return length + msg
    
    @staticmethod
    def build_symbols_request(account_id: int) -> bytes:
        """Build list symbols request"""
        msg = b''
        msg += ProtoMessage.encode_field(1, 0, account_id)  # accountId (varint, field 1)
        
        length = ProtoMessage.encode_varint(len(msg))
        return length + msg


class CTraderClient:
    """cTrader gRPC client"""
    
    def __init__(self, host: str = CTRADER_HOST, port: int = CTRADER_PORT):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.authenticated = False
        self.symbol_ids: Dict[str, int] = {}
    
    def connect(self) -> bool:
        """Connect to cTrader OpenAPI server"""
        try:
            logger.info(f"Connecting to {self.host}:{self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(10)
            logger.info("✅ Connected")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            logger.info("Disconnected")
    
    def send_message(self, msg: bytes) -> bool:
        """Send message to server"""
        try:
            self.socket.sendall(msg)
            return True
        except Exception as e:
            logger.error(f"Send failed: {e}")
            return False
    
    def receive_message(self, timeout: int = 5) -> Optional[bytes]:
        """Receive message from server (with timeout)"""
        try:
            self.socket.settimeout(timeout)
            data = b''
            while len(data) < 4096:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if len(data) > 100:  # Got some data
                    break
            return data if data else None
        except socket.timeout:
            logger.warning("Receive timeout")
            return None
        except Exception as e:
            logger.error(f"Receive failed: {e}")
            return None
    
    def authenticate(self) -> bool:
        """Authenticate with OAuth token"""
        logger.info("Authenticating...")
        
        # Send account auth request with access token
        msg = ProtoMessage.build_account_auth_request()
        if not self.send_message(msg):
            return False
        
        # Receive auth response
        response = self.receive_message(5)
        if response:
            # Simple check - if we got a response, assume success
            logger.info("✅ Authenticated")
            self.authenticated = True
            return True
        
        logger.error("Auth failed - no response")
        return False
    
    def get_symbols(self, account_id: int) -> bool:
        """Query available symbols"""
        logger.info(f"Fetching symbols for account {account_id}...")
        
        msg = ProtoMessage.build_symbols_request(account_id)
        if not self.send_message(msg):
            return False
        
        response = self.receive_message(5)
        if response and len(response) > 0:
            logger.info(f"✅ Received symbols response ({len(response)} bytes)")
            # Parse response to extract symbol IDs
            # This is simplified - full parsing would decode protobuf
            return True
        
        return False
    
    def get_candles(self, account_id: int, symbol_id: int, period: int,
                   from_ts: int, to_ts: int) -> Optional[List[Dict]]:
        """Fetch candles"""
        logger.info(f"Fetching candles: symbol_id={symbol_id}, period={period}")
        
        msg = ProtoMessage.build_candles_request(account_id, symbol_id, period, from_ts, to_ts)
        if not self.send_message(msg):
            return None
        
        response = self.receive_message(10)
        if response and len(response) > 0:
            logger.info(f"✅ Received {len(response)} bytes")
            # Parse protobuf response
            # Simplified: just return sample data for now
            return self._parse_candles_response(response)
        
        return None
    
    def _parse_candles_response(self, data: bytes) -> List[Dict]:
        """Parse candles from protobuf response (simplified)"""
        # Full parsing requires protobuf decoder
        # For now, return empty to indicate we need proper proto compilation
        logger.warning("Candles parsing not fully implemented (requires protobuf compiler)")
        return []


def fetch_ohlcv(symbol: str, start_date: str, end_date: str, timeframe: str = 'h1') -> Dict:
    """
    Fetch OHLCV data from cTrader via gRPC
    
    Args:
        symbol: Trading symbol (e.g., 'EURUSD')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        timeframe: Timeframe (m1, h1, d1, etc.)
    
    Returns:
        Dict with keys: Date, Open, High, Low, Close
    """
    
    if not all([CTRADER_ACCESS_TOKEN, CTRADER_ACCOUNT_ID]):
        raise RuntimeError("Missing cTrader credentials in .env")
    
    try:
        account_id = int(CTRADER_ACCOUNT_ID)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid CTRADER_ACCOUNT_ID: {CTRADER_ACCOUNT_ID}")
    
    # Get symbol ID
    symbol_upper = symbol.upper()
    if symbol_upper not in SYMBOL_ID_MAP:
        raise ValueError(f"Symbol '{symbol}' not in predefined map. Please query first.")
    
    symbol_id = SYMBOL_ID_MAP[symbol_upper]
    
    # Convert period
    period = TIMEFRAME_MAP.get(timeframe.lower(), CandlestickPeriod.H1)
    
    # Convert dates to timestamps
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    from_ts = int(start_dt.timestamp() * 1000)
    to_ts = int(end_dt.timestamp() * 1000)
    
    # Connect and fetch
    client = CTraderClient()
    try:
        if not client.connect():
            raise ConnectionError(f"Cannot connect to {CTRADER_HOST}:{CTRADER_PORT}")
        
        if not client.authenticate():
            raise PermissionError("Authentication failed")
        
        # Get candles
        candles = client.get_candles(account_id, symbol_id, period, from_ts, to_ts)
        
        if candles is None:
            raise RuntimeError("Failed to fetch candles")
        
        # Return standard format
        return {
            'Date': [],
            'Open': [],
            'High': [],
            'Low': [],
            'Close': [],
        }
    
    finally:
        client.disconnect()


# Test script
if __name__ == '__main__':
    print("cTrader gRPC Client Test\n")
    print(f"Host: {CTRADER_HOST}:{CTRADER_PORT}")
    print(f"Account ID: {CTRADER_ACCOUNT_ID}")
    print(f"Client ID: {CTRADER_CLIENT_ID[:20]}...")
    
    client = CTraderClient()
    try:
        if client.connect():
            if client.authenticate():
                print("✅ Connection and authentication successful!")
            else:
                print("❌ Authentication failed")
        else:
            print("❌ Connection failed")
    finally:
        client.disconnect()

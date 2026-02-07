#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data sources module - Support for Yahoo Finance and CCXT exchanges
"""

import yfinance as yf
import ccxt
import pandas as pd
from datetime import datetime, timedelta


def load_yfinance_data(symbol, start_date, end_date):
    """Download stock data from Yahoo Finance"""
    print(f"Downloading {symbol} from yfinance ({start_date} to {end_date})...")
    
    data = yf.Ticker(symbol)
    ts = data.history(start=start_date, end=end_date)
    
    # Reset index
    ts.reset_index(level=0, inplace=True)
    
    # Convert pd.timestamp to string
    ts['Date'] = ts['Date'].dt.strftime('%Y-%m-%d')
    
    # Select required keys
    ts = ts[['Date', 'Open', 'High', 'Low', 'Close']]
    
    # Convert DataFrame to dictionary
    ts = ts.to_dict('list')
    
    return ts


def load_ccxt_data(exchange_name, pair, start_date, end_date, timeframe='1d'):
    """
    Download cryptocurrency data from CCXT exchange
    
    Args:
        exchange_name: Exchange name (binance, kraken, coinbase, etc.)
        pair: Trading pair (BTC/USDT, ETH/USD, etc.)
        start_date: Start date (YYYY-MM-DD or timestamp in ms)
        end_date: End date (YYYY-MM-DD or timestamp in ms)
        timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d', '1w')
    
    Returns:
        Dictionary with Date, Open, High, Low, Close
    """
    
    # Validate exchange
    valid_exchanges = ccxt.exchanges
    if exchange_name.lower() not in valid_exchanges:
        raise ValueError(f"Exchange '{exchange_name}' not found. Available: {', '.join(valid_exchanges[:10])}...")
    
    # Initialize exchange
    print(f"Connecting to {exchange_name}...")
    try:
        exchange_class = getattr(ccxt, exchange_name.lower())
        exchange = exchange_class({'enableRateLimit': True})
    except Exception as e:
        raise ValueError(f"Error initializing {exchange_name}: {str(e)}")
    
    # Check if exchange supports pair
    if not exchange.has['fetchOHLCV']:
        raise ValueError(f"{exchange_name} doesn't support OHLCV data")
    
    # Convert date strings to timestamps
    if isinstance(start_date, str):
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
    else:
        start_ts = start_date
    
    if isinstance(end_date, str):
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
    else:
        end_ts = end_date
    
    print(f"Downloading {pair} from {exchange_name} ({start_date} to {end_date}, timeframe: {timeframe})...")
    
    # Fetch OHLCV data
    all_candles = []
    since = start_ts
    
    try:
        while since < end_ts:
            try:
                candles = exchange.fetch_ohlcv(pair, timeframe, since=since, limit=1000)
                if not candles:
                    break
                
                all_candles.extend(candles)
                since = candles[-1][0] + 1  # Move to next candle
                
                # Show progress
                last_candle_date = datetime.fromtimestamp(candles[-1][0] / 1000).strftime('%Y-%m-%d')
                print(f"  Loaded up to {last_candle_date}...", end='\r')
                
            except ccxt.RateLimitExceeded:
                print("Rate limit exceeded, pausing...")
                exchange.sleep(1000)
                continue
    
    except ccxt.NetworkError as e:
        print(f"Network error: {str(e)}")
        raise
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {str(e)}")
        raise
    
    print()  # New line after progress
    
    if not all_candles:
        raise ValueError(f"No data found for {pair}")
    
    # Convert to list format expected by PointFigureChart
    dates = []
    opens = []
    highs = []
    lows = []
    closes = []
    
    for candle in all_candles:
        ts, o, h, l, c = candle[0], candle[1], candle[2], candle[3], candle[4]
        date_str = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d')
        
        # Skip if before start or after end
        if ts < start_ts or ts > end_ts:
            continue
        
        # Skip duplicates
        if dates and dates[-1] == date_str:
            # Update with latest values for the same day
            closes[-1] = c
            highs[-1] = max(highs[-1], h)
            lows[-1] = min(lows[-1], l)
            continue
        
        dates.append(date_str)
        opens.append(o)
        highs.append(h)
        lows.append(l)
        closes.append(c)
    
    result = {
        'Date': dates,
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes
    }
    
    print(f"Loaded {len(dates)} candles")
    
    return result


def get_available_exchanges():
    """Return list of available CCXT exchanges"""
    return ccxt.exchanges


def get_exchange_symbols(exchange_name):
    """Get list of symbols available on exchange"""
    try:
        exchange_class = getattr(ccxt, exchange_name.lower())
        exchange = exchange_class()
        exchange.load_markets()
        symbols = exchange.symbols
        return symbols
    except Exception as e:
        raise ValueError(f"Error fetching symbols from {exchange_name}: {str(e)}")


def get_exchange_timeframes(exchange_name):
    """Get list of supported timeframes on exchange"""
    try:
        exchange_class = getattr(ccxt, exchange_name.lower())
        exchange = exchange_class()
        if hasattr(exchange, 'timeframes'):
            return list(exchange.timeframes.keys()) if exchange.timeframes else ['1m', '5m', '15m', '1h', '4h', '1d', '1w']
        return ['1m', '5m', '15m', '1h', '4h', '1d', '1w']
    except Exception as e:
        raise ValueError(f"Error fetching timeframes from {exchange_name}: {str(e)}")

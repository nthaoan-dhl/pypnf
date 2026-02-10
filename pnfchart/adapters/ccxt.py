#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CCXT Data Adapter

Provides cryptocurrency data loading from 111+ exchanges via CCXT library.
Implements CCXT best practices from SKILL.md.
"""

import ccxt
from datetime import datetime


def load_ccxt_data(exchange_name, pair, start_date, end_date, timeframe='1d'):
    """
    Download cryptocurrency data from CCXT exchange (REST API - sync)
    
    Args:
        exchange_name: Exchange name (binance, kraken, coinbase, etc.)
        pair: Trading pair (BTC/USDT, ETH/USD, etc.)
        start_date: Start date (YYYY-MM-DD or timestamp in ms)
        end_date: End date (YYYY-MM-DD or timestamp in ms)
        timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d', '1w')
    
    Returns:
        Dictionary with Date, Open, High, Low, Close
    
    Best practices:
        - Uses enableRateLimit for automatic throttling
        - Loads markets to validate symbol
        - Proper error handling per CCXT hierarchy
        - Retry logic for network errors
    """
    
    # Validate exchange
    valid_exchanges = ccxt.exchanges
    if exchange_name.lower() not in valid_exchanges:
        raise ValueError(
            f"Exchange '{exchange_name}' not found.\n"
            f"Available exchanges: {', '.join(sorted(valid_exchanges[:20]))}...\n"
            f"See full list: https://github.com/ccxt/ccxt#supported-exchanges"
        )
    
    # Initialize exchange with best practices
    print(f"Connecting to {exchange_name}...")
    try:
        exchange_class = getattr(ccxt, exchange_name.lower())
        exchange = exchange_class({
            'enableRateLimit': True,  # Critical: automatic rate limiting
            'timeout': 30000,          # 30 second timeout
        })
    except AttributeError:
        raise ValueError(f"Exchange '{exchange_name}' not supported by CCXT")
    except Exception as e:
        raise ValueError(f"Error initializing {exchange_name}: {str(e)}")
    
    # Check if exchange supports OHLCV
    if not exchange.has.get('fetchOHLCV', False):
        raise ValueError(
            f"{exchange_name} doesn't support OHLCV data (candlesticks).\n"
            f"Try a different exchange or check exchange.has for supported features."
        )
    
    # Load markets (recommended practice)
    print(f"Loading markets from {exchange_name}...")
    try:
        exchange.load_markets()
    except ccxt.NetworkError as e:
        raise ValueError(f"Network error loading markets: {str(e)}. Check your connection.")
    except ccxt.ExchangeError as e:
        raise ValueError(f"Exchange error loading markets: {str(e)}")
    
    # Validate symbol exists
    if pair not in exchange.markets:
        available_symbols = [s for s in exchange.symbols if pair.split('/')[0] in s][:10]
        raise ValueError(
            f"Symbol '{pair}' not found on {exchange_name}.\n"
            f"Similar symbols: {', '.join(available_symbols) if available_symbols else 'None'}\n"
            f"Use get_exchange_symbols('{exchange_name}') to see all available symbols."
        )
    
    # Validate timeframe
    if hasattr(exchange, 'timeframes') and exchange.timeframes:
        if timeframe not in exchange.timeframes:
            raise ValueError(
                f"Timeframe '{timeframe}' not supported by {exchange_name}.\n"
                f"Supported timeframes: {', '.join(exchange.timeframes.keys())}"
            )
    
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
    
    # Fetch OHLCV data with retry logic
    all_candles = []
    since = start_ts
    max_retries = 3
    
    try:
        while since < end_ts:
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    candles = exchange.fetch_ohlcv(pair, timeframe, since=since, limit=1000)
                    if not candles:
                        break
                    
                    all_candles.extend(candles)
                    since = candles[-1][0] + 1  # Move to next candle
                    
                    # Show progress
                    last_candle_date = datetime.fromtimestamp(candles[-1][0] / 1000).strftime('%Y-%m-%d')
                    print(f"  Loaded up to {last_candle_date}...", end='\r')
                    break  # Success, exit retry loop
                    
                except ccxt.RateLimitExceeded as e:
                    print(f"\n⚠️  Rate limit exceeded. Waiting before retry...")
                    exchange.sleep(2000)  # Wait 2 seconds
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise ValueError(
                            f"Rate limit exceeded after {max_retries} retries.\n"
                            f"The exchange is throttling requests. Try again later or use a longer timeframe."
                        ) from e
                    continue
                    
                except ccxt.NetworkError as e:
                    # Retry on network errors (recoverable)
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise ValueError(
                            f"Network error after {max_retries} retries: {str(e)}\n"
                            f"Check your internet connection and try again."
                        ) from e
                    print(f"\n⚠️  Network error. Retry {retry_count}/{max_retries}...")
                    exchange.sleep(1000 * retry_count)  # Exponential backoff
                    continue
            
            if not candles:
                break
    
    except ccxt.AuthenticationError as e:
        # Non-recoverable: don't retry
        raise ValueError(
            f"Authentication error: {str(e)}\n"
            f"Check your API credentials if using private endpoints."
        ) from e
    except ccxt.InsufficientFunds as e:
        raise ValueError(f"Insufficient funds: {str(e)}") from e
    except ccxt.InvalidOrder as e:
        raise ValueError(f"Invalid parameters: {str(e)}") from e
    except ccxt.ExchangeNotAvailable as e:
        raise ValueError(
            f"Exchange not available: {str(e)}\n"
            f"The exchange may be under maintenance. Try again later."
        ) from e
    except ccxt.ExchangeError as e:
        # Generic exchange error (non-recoverable)
        raise ValueError(
            f"Exchange error: {str(e)}\n"
            f"This error is specific to {exchange_name}. Check the exchange's API status."
        ) from e
    except ccxt.NetworkError as e:
        # Final network error (all retries exhausted)
        raise ValueError(f"Network error: {str(e)}") from e
    
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




# Helper functions for exchange queries
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


# Alias for consistency
load_data = load_ccxt_data

__all__ = ['load_data', 'load_ccxt_data', 'get_available_exchanges', 'get_exchange_symbols', 'get_exchange_timeframes']

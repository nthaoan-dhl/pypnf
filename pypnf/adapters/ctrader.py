#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cTrader Data Adapter

Provides data loading from cTrader via provider module or CSV files.
"""

import os
import sys
import importlib
from datetime import datetime

# Add providers directory to sys.path to find ctrader_provider module
providers_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'providers'))
if os.path.exists(providers_dir) and providers_dir not in sys.path:
    sys.path.insert(0, providers_dir)

# Also add workspace root for backward compatibility
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)


_CTRADER_TF_MAP = {
    '1m': 'm1',
    'm1': 'm1',
    '5m': 'm5',
    'm5': 'm5',
    '15m': 'm15',
    'm15': 'm15',
    '30m': 'm30',
    'm30': 'm30',
    '1h': 'h1',
    'h1': 'h1',
    '4h': 'h4',
    'h4': 'h4',
    '1d': 'd1',
    'd1': 'd1',
}


def _normalize_ctrader_timeframe(timeframe):
    if timeframe is None:
        return 'd1'
    tf = str(timeframe).lower()
    return _CTRADER_TF_MAP.get(tf, tf)


def load_ctrader_data(symbol, start_date, end_date, timeframe='d1', provider_module=None, csv_path=None):
    """
    Download data from cTrader via a provider module.

    The provider module must expose:
        fetch_ohlcv(symbol, start_date, end_date, timeframe) -> list or dict

    If CTRADER_CSV_PATH is set (or csv_path provided), the default provider
    can load OHLCV from a CSV file.
    """

    module_name = provider_module or os.getenv('CTRADER_PROVIDER', 'ctrader_provider')
    if csv_path:
        os.environ['CTRADER_CSV_PATH'] = csv_path

    timeframe = _normalize_ctrader_timeframe(timeframe)

    try:
        provider = importlib.import_module(module_name)
    except Exception as e:
        raise ValueError(f"Failed to load cTrader provider '{module_name}': {str(e)}")

    if not hasattr(provider, 'fetch_ohlcv'):
        raise ValueError(f"Provider '{module_name}' must define fetch_ohlcv()")

    print(f"Loading {symbol} from cTrader provider '{module_name}' ({start_date} to {end_date}, timeframe: {timeframe})...")
    ohlcv = provider.fetch_ohlcv(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        timeframe=timeframe
    )

    if isinstance(ohlcv, dict):
        return ohlcv

    if not ohlcv:
        raise ValueError(f"No data found for {symbol}")

    dates = []
    opens = []
    highs = []
    lows = []
    closes = []

    start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
    end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)

    for candle in ohlcv:
        ts, o, h, l, c = candle[0], candle[1], candle[2], candle[3], candle[4]
        if ts < start_ts or ts > end_ts:
            continue
        date_str = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d')

        if dates and dates[-1] == date_str:
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




# Alias for consistency
load_data = load_ctrader_data

__all__ = ['load_data', 'load_ctrader_data']

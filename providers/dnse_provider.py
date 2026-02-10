#!/usr/bin/env python3
"""
DNSE Lightspeed snapshot provider.

Configure via environment variables:
- DNSE_SNAPSHOT_URL: Full URL, can include {symbol} placeholder.
- DNSE_BASE_URL and DNSE_SNAPSHOT_ENDPOINT: Base + endpoint if full URL not set.
- DNSE_API_KEY: Optional bearer token.
- DNSE_TIMEOUT: Request timeout in seconds (default: 10).
- DNSE_SYMBOL_PARAM: Query param name for symbol (default: symbol).
- DNSE_MARKET_PARAM: Query param name for market (optional).
- DNSE_TIMEFRAME_PARAM: Query param name for timeframe (optional).
"""

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime


def _build_snapshot_url(symbol, base_url, endpoint, snapshot_url, params):
    if snapshot_url:
        if '{symbol}' in snapshot_url:
            return snapshot_url.format(symbol=symbol)
        return snapshot_url

    if not base_url or not endpoint:
        raise ValueError("DNSE snapshot URL not configured")

    base_url = base_url.rstrip('/')
    endpoint = endpoint.lstrip('/')
    url = f"{base_url}/{endpoint}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    return url


def _http_get_json(url, headers, timeout):
    request = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode('utf-8')
    return json.loads(raw)


def _extract_snapshot(payload):
    if payload is None:
        raise ValueError("Empty DNSE response")

    if isinstance(payload, dict):
        if 'data' in payload:
            payload = payload['data']
        elif 'result' in payload:
            payload = payload['result']

    if isinstance(payload, list):
        payload = payload[0] if payload else None

    if not isinstance(payload, dict):
        raise ValueError("Unexpected DNSE response format")

    def _pick(keys, default=None):
        for key in keys:
            if key in payload:
                return payload[key]
        return default

    timestamp = _pick(['timestamp', 'time', 't', 'tradingDate', 'date'])
    price = _pick(['close', 'c', 'last', 'price', 'lastPrice'])
    open_price = _pick(['open', 'o'], price)
    high_price = _pick(['high', 'h'], price)
    low_price = _pick(['low', 'l'], price)

    if price is None:
        raise ValueError("DNSE snapshot missing price fields")

    if timestamp is None:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d')
    else:
        try:
            timestamp = datetime.fromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d')
        except Exception:
            timestamp = str(timestamp)[:10]

    return {
        'Date': [timestamp],
        'Open': [float(open_price)],
        'High': [float(high_price)],
        'Low': [float(low_price)],
        'Close': [float(price)],
    }


def fetch_snapshot(symbol, timeframe=None, market=None, extra_params=None):
    """Fetch a single snapshot candle and return a dict with Date/Open/High/Low/Close."""
    base_url = os.getenv('DNSE_BASE_URL', '')
    endpoint = os.getenv('DNSE_SNAPSHOT_ENDPOINT', '')
    snapshot_url = os.getenv('DNSE_SNAPSHOT_URL', '')
    api_key = os.getenv('DNSE_API_KEY', '')
    timeout = int(os.getenv('DNSE_TIMEOUT', '10'))

    symbol_param = os.getenv('DNSE_SYMBOL_PARAM', 'symbol')
    market_param = os.getenv('DNSE_MARKET_PARAM', '')
    timeframe_param = os.getenv('DNSE_TIMEFRAME_PARAM', '')

    params = {}
    if symbol_param:
        params[symbol_param] = symbol
    if market_param and market:
        params[market_param] = market
    if timeframe_param and timeframe:
        params[timeframe_param] = timeframe
    if extra_params:
        params.update(extra_params)

    url = _build_snapshot_url(symbol, base_url, endpoint, snapshot_url, params)

    headers = {'Accept': 'application/json'}
    if api_key:
        headers['Authorization'] = f"Bearer {api_key}"

    payload = _http_get_json(url, headers, timeout)
    return _extract_snapshot(payload)

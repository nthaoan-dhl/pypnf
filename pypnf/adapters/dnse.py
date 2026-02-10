#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DNSE Data Adapter

Provides data loading from DNSE Lightspeed via provider module.
Can be combined with vnstock historical data.
"""

import os
import importlib
from pypnf.adapters.vnstock import load_data as load_vnstock_data


def load_dnse_data(symbol, start_date, end_date, timeframe='1m', provider_module=None, include_history=True):
    """
    Download market data from DNSE via a provider module.

    Provider module must expose:
        fetch_snapshot(symbol, timeframe=None, **kwargs) -> dict

    If include_history is True, vnstock is used to fetch historical OHLCV
    and the DNSE snapshot is appended when available.
    """

    module_name = provider_module or os.getenv('DNSE_PROVIDER', 'dnse_provider')
    try:
        provider = importlib.import_module(module_name)
    except Exception as e:
        raise ValueError(f"Failed to load DNSE provider '{module_name}': {str(e)}")

    if not hasattr(provider, 'fetch_snapshot'):
        raise ValueError(f"Provider '{module_name}' must define fetch_snapshot()")

    history = None
    if include_history:
        history = load_vnstock_data(symbol, start_date, end_date, interval='1D')

    snapshot = provider.fetch_snapshot(symbol=symbol, timeframe=timeframe)
    if not snapshot:
        return history if history is not None else snapshot

    if history is None:
        return snapshot

    # Append snapshot if it is newer than the last history point.
    try:
        last_date = history['Date'][-1]
        snap_date = snapshot['Date'][-1]
        if snap_date > last_date:
            for key in ['Date', 'Open', 'High', 'Low', 'Close']:
                history[key].extend(snapshot[key])
    except Exception:
        return history

    return history




# Alias for consistency  
load_data = load_dnse_data

__all__ = ['load_data', 'load_dnse_data']

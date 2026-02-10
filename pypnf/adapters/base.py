#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base Adapter

Common utilities for all data adapters.
"""

import pandas as pd


def normalize_ohlc_dataframe(df):
    """Normalize a pandas DataFrame to Date/Open/High/Low/Close dict."""
    if df is None or df.empty:
        raise ValueError("No data returned")

    columns = {col.lower(): col for col in df.columns}
    date_col = None
    for candidate in ['date', 'time', 'datetime', 'tradingdate']:
        if candidate in columns:
            date_col = columns[candidate]
            break

    if date_col is None:
        if df.index.name and df.index.name.lower() in ['date', 'time', 'datetime']:
            df = df.reset_index()
            date_col = df.columns[0]
        else:
            raise ValueError("Unable to find a date column in data")

    o_col = columns.get('open')
    h_col = columns.get('high')
    l_col = columns.get('low')
    c_col = columns.get('close')

    if not all([o_col, h_col, l_col, c_col]):
        raise ValueError("Data missing OHLC columns")

    df = df[[date_col, o_col, h_col, l_col, c_col]].copy()
    df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')

    return {
        'Date': df[date_col].tolist(),
        'Open': df[o_col].tolist(),
        'High': df[h_col].tolist(),
        'Low': df[l_col].tolist(),
        'Close': df[c_col].tolist(),
    }


__all__ = ['normalize_ohlc_dataframe']

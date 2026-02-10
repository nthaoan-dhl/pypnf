#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VNStock Data Adapter

Provides data loading from Vietnam stock market via vnstock library.
"""

from pypnf.adapters.base import normalize_ohlc_dataframe


def load_data(symbol, start_date, end_date, interval='1D'):
    """
    Download Vietnam stock data via vnstock (historical).
    
    Args:
        symbol: Stock symbol (e.g., 'FPT', 'VNM')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        interval: Interval ('1D', '1W', '1M')
    
    Returns:
        Dictionary with Date, Open, High, Low, Close
    
    Examples:
        >>> data = load_data('FPT', '2024-01-01', '2024-12-31')
    """
    try:
        from vnstock import stock_historical_data
    except ImportError as e:
        raise ValueError(
            "vnstock is not installed. Install with: pip install vnstock"
        ) from e

    df = stock_historical_data(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        resolution=interval,
        type='stock'
    )

    return normalize_ohlc_dataframe(df)


__all__ = ['load_data']

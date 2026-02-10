#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Yahoo Finance Data Adapter

Provides data loading from Yahoo Finance for stocks and indices.
"""

import yfinance as yf


def load_data(symbol, start_date, end_date):
    """
    Download stock data from Yahoo Finance.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', '^SPX')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        Dictionary with Date, Open, High, Low, Close
    
    Examples:
        >>> data = load_data('AAPL', '2024-01-01', '2024-12-31')
        >>> len(data['Date'])
        252
    """
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


__all__ = ['load_data']

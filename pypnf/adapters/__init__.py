"""
pypnf.adapters - Data Source Adapters

This package contains adapters for various data sources:
- yfinance: Yahoo Finance (stocks, indices)
- ccxt: Cryptocurrency exchanges (111+ exchanges)
- ctrader: cTrader platform
- vnstock: Vietnam stock market
- dnse: DNSE Lightspeed
"""

from pypnf.adapters import yfinance, ccxt, ctrader, vnstock, dnse

# Re-export main loading functions with source prefix
from pypnf.adapters.yfinance import load_data as load_yfinance_data
from pypnf.adapters.ccxt import load_ccxt_data, get_available_exchanges, get_exchange_symbols, get_exchange_timeframes
from pypnf.adapters.ctrader import load_ctrader_data
from pypnf.adapters.vnstock import load_data as load_vnstock_data
from pypnf.adapters.dnse import load_dnse_data

__all__ = [
    # Modules
    'yfinance',
    'ccxt',
    'ctrader',
    'vnstock',
    'dnse',
    # Functions
    'load_yfinance_data',
    'load_ccxt_data',
    'load_ctrader_data',
    'load_vnstock_data',
    'load_dnse_data',
    # Helpers
    'get_available_exchanges',
    'get_exchange_symbols',
    'get_exchange_timeframes',
]

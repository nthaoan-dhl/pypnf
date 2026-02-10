# -*- coding: utf-8 -*-
#
# pyPnF
# A Package for Point and Figure Charting
# https://github.com/swaschke/pypnf
#
# Copyright 2021 Stefan Waschke
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
pyPnF - Python Point & Figure Charting Library

A comprehensive library for creating Point & Figure charts with support
for multiple data sources including stocks, cryptocurrencies, and forex.

Architecture:
- core: Point & Figure calculation engine  
- adapters: Data source adapters (yfinance, ccxt, ctrader, vnstock, dnse)
- app: CLI application

Examples:
    >>> from pypnf import PointFigureChart
    >>> from pypnf.adapters import load_yfinance_data
    >>> 
    >>> data = load_yfinance_data('AAPL', '2024-01-01', '2024-12-31')
    >>> pnf = PointFigureChart(data, method='h/l', reversal=3)
    >>> print(pnf)
"""

# Core exports
from pypnf.core import PointFigureChart, dataset

# Adapter exports (for convenience)
from pypnf.adapters import (
    load_yfinance_data,
    load_ccxt_data,
    load_ctrader_data,
    load_vnstock_data,
    load_dnse_data,
)

__version__ = "1.0.0"
__author__ = "pypnf contributors"

__all__ = [
    # Core
    'PointFigureChart',
    'dataset',
    # Adapters
    'load_yfinance_data',
    'load_ccxt_data',
    'load_ctrader_data',
    'load_vnstock_data',
    'load_dnse_data',
]

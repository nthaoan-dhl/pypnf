#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pnfchart.py - Convenience wrapper for pypnf CLI

This file maintains backward compatibility with the original CLI interface.
The actual implementation is now in pypnf.app.cli module.

Usage:
    python pnfchart.py [SYMBOL] [OPTIONS]
    
Examples:
    python pnfchart.py AMD
    python pnfchart.py BTC/USDT --source ccxt --exchange binance
    python pnfchart.py EURUSD --source ctrader
"""

if __name__ == '__main__':
    from pnfchart.app.cli import main
    main()

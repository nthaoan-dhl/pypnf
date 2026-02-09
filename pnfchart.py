#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Point & Figure Chart Generator - Support for stocks (yfinance), crypto (CCXT), and cTrader
Usage: python pnfchart.py [SYMBOL] [OPTIONS]
Example: python pnfchart.py AMD
         python pnfchart.py BTC/USDT --source ccxt --exchange binance
         python pnfchart.py EURUSD --source ctrader
"""

import argparse
from pypnf import PointFigureChart
from datetime import date
from data_sources import (
    load_yfinance_data,
    load_ccxt_data,
    load_ctrader_data,
    load_dnse_data,
    load_vnstock_data,
)

# Default Configuration
DEFAULT_SYMBOL = 'AMD'
DEFAULT_START_DATE = '2024-01-01'  # Changed from 2010 to reduce data load
DEFAULT_END_DATE = date.today().strftime('%Y-%m-%d')  # Today's date
DEFAULT_METHOD = 'h/l'           # 'cl', 'h/l', 'l/h', 'hlc', 'ohlc'
DEFAULT_REVERSAL = 3            # number of boxes for reversal
DEFAULT_BOXSIZE = 1             # percentage value for 'cla' scaling
DEFAULT_SCALING = 'cla'         # 'abs', 'atr', 'cla', 'log'
DEFAULT_SOURCE = 'yfinance'     # 'yfinance', 'ccxt', 'ctrader', 'vnstock', 'dnse'
DEFAULT_EXCHANGE = 'binance'    # CCXT exchange name
DEFAULT_TIMEFRAME = '1d'        # Candle timeframe (CCXT/ctrader)
DEFAULT_CTRADER_PROVIDER = 'ctrader_provider'

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Create Point & Figure charts from stock (yfinance) or crypto (CCXT) data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stock data (Yahoo Finance)
  python pnfchart.py AMD
  python pnfchart.py AAPL --method cl --reversal 2
  python pnfchart.py TSLA --start 2020-01-01 --scaling log --boxsize 1
  
  # Crypto data (CCXT)
  python pnfchart.py BTC/USDT --source ccxt --exchange binance
  python pnfchart.py ETH/USDT --source ccxt --exchange binance --timeframe 1h
  python pnfchart.py BTC/USD --source ccxt --exchange kraken

  # cTrader data
  python pnfchart.py EURUSD --source ctrader
  python pnfchart.py XAUUSD --source ctrader --timeframe h1
        """
    )
    
    parser.add_argument('symbol', nargs='?', default=DEFAULT_SYMBOL,
                        help=f'Stock/Crypto symbol (default: {DEFAULT_SYMBOL}). For crypto: use BTC/USDT format')
    parser.add_argument('--source', default=DEFAULT_SOURCE,
                        choices=['yfinance', 'ccxt', 'ctrader', 'vnstock', 'dnse'],
                        help=f'Data source (default: {DEFAULT_SOURCE})')
    parser.add_argument('--start', dest='start_date', default=DEFAULT_START_DATE,
                        help=f'Start date YYYY-MM-DD (default: {DEFAULT_START_DATE})')
    parser.add_argument('--end', dest='end_date', default=DEFAULT_END_DATE,
                        help=f'End date YYYY-MM-DD (default: {DEFAULT_END_DATE})')
    parser.add_argument('--method', default=DEFAULT_METHOD,
                        choices=['cl', 'h/l', 'l/h', 'hlc', 'ohlc'],
                        help=f'Chart method (default: {DEFAULT_METHOD})')
    parser.add_argument('--reversal', type=int, default=DEFAULT_REVERSAL,
                        help=f'Number of boxes for reversal (default: {DEFAULT_REVERSAL})')
    parser.add_argument('--boxsize', type=float, default=DEFAULT_BOXSIZE,
                        help=f'Box size (default: {DEFAULT_BOXSIZE})')
    parser.add_argument('--scaling', default=DEFAULT_SCALING,
                        choices=['abs', 'atr', 'cla', 'log'],
                        help=f'Scaling method (default: {DEFAULT_SCALING})')
    
    # CCXT-specific arguments
    parser.add_argument('--exchange', default=DEFAULT_EXCHANGE,
                        help=f'CCXT exchange name (default: {DEFAULT_EXCHANGE}). Use with --source ccxt')
    parser.add_argument('--timeframe', default=DEFAULT_TIMEFRAME,
                        help=f'Candle timeframe (CCXT/ctrader). Options: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w or m1, m5, m15, m30, h1, h4, d1')

    # cTrader-specific arguments
    parser.add_argument('--ctrader-provider', default=DEFAULT_CTRADER_PROVIDER,
                        help=f'cTrader provider module (default: {DEFAULT_CTRADER_PROVIDER})')
    parser.add_argument('--ctrader-csv', default=None,
                        help='CSV path for cTrader provider (optional, uses CTRADER_CSV_PATH if set)')

    # DNSE/VNStock-specific arguments
    parser.add_argument('--dnse-provider', default='dnse_provider',
                        help='DNSE provider module (default: dnse_provider)')
    parser.add_argument('--dnse-no-history', action='store_true',
                        help='Skip vnstock historical data when using DNSE')
    parser.add_argument('--vnstock-interval', default='1D',
                        help='VNStock historical interval (default: 1D)')
    
    # Output options
    parser.add_argument('--save', action='store_true',
                        help='Save chart to HTML file')
    parser.add_argument('--show', action='store_true',
                        help='Show chart with matplotlib')
    parser.add_argument('--no-trendlines', action='store_true',
                        help='Skip trendlines calculation')
    parser.add_argument('--no-breakouts', action='store_true',
                        help='Skip breakouts calculation')
    parser.add_argument('--no-signals', action='store_true',
                        help='Skip signals/patterns calculation')
    parser.add_argument('--columns', type=int, default=30,
                        help='Maximum number of columns to display in console (default: 30, use 0 for all columns)')
    
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Load data from appropriate source
        if args.source.lower() == 'ccxt':
            ts = load_ccxt_data(
                exchange_name=args.exchange,
                pair=args.symbol,
                start_date=args.start_date,
                end_date=args.end_date,
                timeframe=args.timeframe
            )
        elif args.source.lower() == 'ctrader':
            ts = load_ctrader_data(
                symbol=args.symbol,
                start_date=args.start_date,
                end_date=args.end_date,
                timeframe=args.timeframe,
                provider_module=args.ctrader_provider,
                csv_path=args.ctrader_csv
            )
        elif args.source.lower() == 'vnstock':
            ts = load_vnstock_data(
                symbol=args.symbol.upper(),
                start_date=args.start_date,
                end_date=args.end_date,
                interval=args.vnstock_interval
            )
        elif args.source.lower() == 'dnse':
            ts = load_dnse_data(
                symbol=args.symbol.upper(),
                start_date=args.start_date,
                end_date=args.end_date,
                timeframe=args.timeframe,
                provider_module=args.dnse_provider,
                include_history=not args.dnse_no_history
            )
        else:
            # Default to yfinance
            ts = load_yfinance_data(
                symbol=args.symbol.upper(),
                start_date=args.start_date,
                end_date=args.end_date
            )
        
        
        # Create Point & Figure Chart
        pnf = PointFigureChart(
            ts=ts,
            method=args.method,
            reversal=args.reversal,
            boxsize=args.boxsize,
            scaling=args.scaling,
            title=args.symbol.upper()
        )
        
        # Set max columns for console display
        pnf.max_columns = args.columns
        
        # Print the chart in console
        print(pnf)
        
        # Get trendlines and print (unless disabled)
        if not args.no_trendlines:
            pnf.get_trendlines()
            print('\n' + '='*80)
            print('CHART WITH TRENDLINES')
            print('='*80)
            print(pnf)
        
        # Get breakouts and print (unless disabled)
        if not args.no_breakouts:
            pnf.get_breakouts()
            print('\n' + '='*80)
            print('CHART WITH TRENDLINES + BREAKOUTS')
            print('='*80)
            print(pnf)
        
        # Get all signals/patterns (unless disabled)
        if not args.no_signals:
            try:
                pnf.get_signals()
                print('\n' + '='*80)
                print('CHART WITH ALL PATTERNS')
                print('='*80)
                print(pnf)
            except Exception as e:
                print(f"\nNote: Signals calculation encountered an issue: {e}")
        
        # Save to HTML if requested
        if args.save:
            filename = f'{args.symbol.replace("/", "_").upper()}_pnf_chart.html'
            pnf.write_html(filename)
            print(f"\nChart saved to {filename}")
        
        # Show plot if requested
        if args.show:
            pnf.show()
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

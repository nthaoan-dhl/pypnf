#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example script to load data from yfinance and create a Point & Figure chart
Usage: python example_yfinance.py [SYMBOL] [OPTIONS]
Example: python example_yfinance.py AMD
         python example_yfinance.py AAPL --method cl --reversal 2
"""

import argparse
import yfinance as yf
from pypnf import PointFigureChart
from datetime import date

# Default Configuration
DEFAULT_SYMBOL = 'AMD'
DEFAULT_START_DATE = '2010-01-01'
DEFAULT_END_DATE = date.today().strftime('%Y-%m-%d')  # Today's date
DEFAULT_METHOD = 'h/l'           # 'cl', 'h/l', 'l/h', 'hlc', 'ohlc'
DEFAULT_REVERSAL = 3            # number of boxes for reversal
DEFAULT_BOXSIZE = 1             # percentage value for 'cla' scaling
DEFAULT_SCALING = 'cla'         # 'abs', 'atr', 'cla', 'log'

def load_yfinance_data(symbol, start_date, end_date):
    """Download data from yfinance and format for PointFigureChart"""
    print(f"Downloading {symbol} data from yfinance ({start_date} to {end_date})...")
    
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

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Create Point & Figure charts from yfinance data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python example_yfinance.py AMD
  python example_yfinance.py AAPL --method cl --reversal 2
  python example_yfinance.py TSLA --start 2020-01-01 --scaling log --boxsize 1
  python example_yfinance.py MSFT --save --show
        """
    )
    
    parser.add_argument('symbol', nargs='?', default=DEFAULT_SYMBOL,
                        help=f'Stock symbol (default: {DEFAULT_SYMBOL})')
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
    
    # Load data
    ts = load_yfinance_data(args.symbol.upper(), args.start_date, args.end_date)
    
    print(f"Loaded {len(ts['Date'])} records")
    print(f"Date range: {ts['Date'][0]} to {ts['Date'][-1]}\n")
    
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
        filename = f'{args.symbol.upper()}_pnf_chart.html'
        pnf.write_html(filename)
        print(f"\nChart saved to {filename}")
    
    # Show plot if requested
    if args.show:
        pnf.show()

if __name__ == '__main__':
    main()

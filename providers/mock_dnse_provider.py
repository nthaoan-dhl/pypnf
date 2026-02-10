
"""Mock DNSE provider for testing"""
from datetime import datetime
import random

def fetch_snapshot(symbol, timeframe=None, market=None, **kwargs):
    """Mock fetch_snapshot that returns random data"""
    
    # Simulate different prices for different symbols
    base_prices = {
        'FPT': 65.0,
        'VNM': 85.0,
        'HPG': 28.0,
        'MSN': 95.0,
        'VCB': 92.0,
        'VIC': 45.0,
    }
    
    base_price = base_prices.get(symbol.upper(), 50.0)
    
    # Random fluctuation
    variation = random.uniform(-2, 2)
    close = base_price + variation
    open_price = close + random.uniform(-1, 1)
    high = max(close, open_price) + random.uniform(0, 1)
    low = min(close, open_price) - random.uniform(0, 1)
    
    return {
        'Date': [datetime.now().strftime('%Y-%m-%d')],
        'Open': [round(open_price, 2)],
        'High': [round(high, 2)],
        'Low': [round(low, 2)],
        'Close': [round(close, 2)]
    }

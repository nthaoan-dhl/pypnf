#!/usr/bin/env python3
"""
CCXT Usage Examples - Following Best Practices from Skill Guide

This script demonstrates proper CCXT usage patterns:
- REST API (sync) for one-time queries
- REST API (async) for concurrent operations
- Error handling hierarchy
- Rate limiting best practices

Usage:
    # Sync (simple, one exchange)
    python example_ccxt_usage.py --mode sync --exchange binance --symbol BTC/USDT
    
    # Async (multiple exchanges concurrently)
    python example_ccxt_usage.py --mode async --symbol BTC/USDT
    
    # Test error handling
    python example_ccxt_usage.py --mode test-errors
"""

import sys
import asyncio
import ccxt
import ccxt.async_support as ccxt_async
from datetime import datetime, timedelta


def example_sync_basic():
    """
    Example 1: Basic sync usage (recommended for simple scripts)
    Following SKILL.md best practices
    """
    print("\n" + "=" * 70)
    print("Example 1: Sync REST API - Basic Usage")
    print("=" * 70)
    
    # Initialize with best practices
    exchange = ccxt.binance({
        'enableRateLimit': True,  # Critical: automatic rate limiting
        'timeout': 30000,
    })
    
    try:
        # Load markets (recommended)
        print("\n1. Loading markets...")
        exchange.load_markets()
        print(f"   ✅ Loaded {len(exchange.markets)} markets")
        
        # Fetch ticker
        print("\n2. Fetching ticker...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"   ✅ BTC/USDT: ${ticker['last']:,.2f}")
        print(f"      Bid: ${ticker['bid']:,.2f}")
        print(f"      Ask: ${ticker['ask']:,.2f}")
        print(f"      24h Volume: {ticker['baseVolume']:,.2f} BTC")
        
        # Fetch order book
        print("\n3. Fetching order book...")
        orderbook = exchange.fetch_order_book('BTC/USDT', limit=5)
        print(f"   ✅ Best bid: ${orderbook['bids'][0][0]:,.2f}")
        print(f"      Best ask: ${orderbook['asks'][0][0]:,.2f}")
        print(f"      Spread: ${orderbook['asks'][0][0] - orderbook['bids'][0][0]:.2f}")
        
        # Fetch recent trades
        print("\n4. Fetching recent trades...")
        trades = exchange.fetch_trades('BTC/USDT', limit=5)
        print(f"   ✅ Last 5 trades:")
        for trade in trades[-5:]:
            side_icon = "🟢" if trade['side'] == 'buy' else "🔴"
            print(f"      {side_icon} ${trade['price']:,.2f} × {trade['amount']:.4f}")
        
        # Fetch OHLCV
        print("\n5. Fetching OHLCV (candlesticks)...")
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=24)
        print(f"   ✅ Last 24 hours:")
        latest = ohlcv[-1]
        ts = datetime.fromtimestamp(latest[0] / 1000)
        print(f"      Time:  {ts.strftime('%Y-%m-%d %H:%M')}")
        print(f"      Open:  ${latest[1]:,.2f}")
        print(f"      High:  ${latest[2]:,.2f}")
        print(f"      Low:   ${latest[3]:,.2f}")
        print(f"      Close: ${latest[4]:,.2f}")
        
        print("\n✅ Example completed successfully!")
        
    except ccxt.NetworkError as e:
        print(f"\n❌ Network error (recoverable - retry): {e}")
    except ccxt.ExchangeError as e:
        print(f"\n❌ Exchange error (non-recoverable): {e}")
    except Exception as e:
        print(f"\n❌ Unknown error: {e}")


async def example_async_basic():
    """
    Example 2: Async usage for concurrent operations
    """
    print("\n" + "=" * 70)
    print("Example 2: Async REST API - Single Exchange")
    print("=" * 70)
    
    # Use async_support for async operations
    exchange = ccxt_async.binance({
        'enableRateLimit': True,
        'timeout': 30000,
    })
    
    try:
        # Concurrent operations
        print("\n1. Fetching data concurrently...")
        
        tasks = [
            exchange.load_markets(),
            exchange.fetch_ticker('BTC/USDT'),
            exchange.fetch_ticker('ETH/USDT'),
            exchange.fetch_ticker('SOL/USDT'),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        markets, btc_ticker, eth_ticker, sol_ticker = results
        
        if isinstance(btc_ticker, Exception):
            print(f"   ❌ BTC error: {btc_ticker}")
        else:
            print(f"   ✅ BTC/USDT: ${btc_ticker['last']:,.2f}")
        
        if isinstance(eth_ticker, Exception):
            print(f"   ❌ ETH error: {eth_ticker}")
        else:
            print(f"   ✅ ETH/USDT: ${eth_ticker['last']:,.2f}")
        
        if isinstance(sol_ticker, Exception):
            print(f"   ❌ SOL error: {sol_ticker}")
        else:
            print(f"   ✅ SOL/USDT: ${sol_ticker['last']:,.2f}")
        
        print("\n✅ Async example completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Critical: always close async exchange!
        await exchange.close()
        print("   ✅ Exchange connection closed")


async def example_async_multiple_exchanges():
    """
    Example 3: Multiple exchanges concurrently (async advantage)
    """
    print("\n" + "=" * 70)
    print("Example 3: Async REST API - Multiple Exchanges")
    print("=" * 70)
    
    # Initialize multiple exchanges
    exchanges = {
        'Binance': ccxt_async.binance({'enableRateLimit': True}),
        'Coinbase': ccxt_async.coinbase({'enableRateLimit': True}),
        'Kraken': ccxt_async.kraken({'enableRateLimit': True}),
    }
    
    try:
        print("\n1. Fetching BTC/USDT price from multiple exchanges...")
        
        tasks = []
        for name, ex in exchanges.items():
            # Use BTC/USD for exchanges that use USD
            symbol = 'BTC/USD' if name == 'Coinbase' else 'BTC/USDT'
            tasks.append(ex.fetch_ticker(symbol))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for (name, ex), result in zip(exchanges.items(), results):
            if isinstance(result, Exception):
                print(f"   ❌ {name}: {type(result).__name__}")
            else:
                print(f"   ✅ {name}: ${result['last']:,.2f}")
        
        # Find arbitrage opportunities
        prices = [r['last'] for r in results if not isinstance(r, Exception)]
        if len(prices) >= 2:
            spread = max(prices) - min(prices)
            spread_pct = (spread / min(prices)) * 100
            print(f"\n   💡 Price spread: ${spread:.2f} ({spread_pct:.2f}%)")
        
        print("\n✅ Multi-exchange example completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Close all exchanges
        for name, ex in exchanges.items():
            await ex.close()
        print("   ✅ All exchange connections closed")


def example_error_handling():
    """
    Example 4: Proper error handling following CCXT hierarchy
    """
    print("\n" + "=" * 70)
    print("Example 4: Error Handling Best Practices")
    print("=" * 70)
    
    exchange = ccxt.binance({'enableRateLimit': True})
    
    # Test 1: Invalid symbol
    print("\n1. Testing invalid symbol...")
    try:
        exchange.load_markets()
        ticker = exchange.fetch_ticker('INVALID/SYMBOL')
    except ccxt.BadSymbol as e:
        print(f"   ✅ Caught BadSymbol: {e}")
    except ccxt.ExchangeError as e:
        print(f"   ✅ Caught ExchangeError: {e}")
    
    # Test 2: Checking capabilities
    print("\n2. Checking exchange capabilities...")
    print(f"   fetchOHLCV: {exchange.has.get('fetchOHLCV', False)}")
    print(f"   fetchTicker: {exchange.has.get('fetchTicker', False)}")
    print(f"   fetchBalance: {exchange.has.get('fetchBalance', False)}")
    
    # Test 3: Market validation
    print("\n3. Validating symbol before use...")
    symbol = 'BTC/USDT'
    if symbol in exchange.markets:
        print(f"   ✅ {symbol} is valid")
        market = exchange.markets[symbol]
        print(f"      Min amount: {market['limits']['amount']['min']}")
        print(f"      Min cost: {market['limits']['cost']['min']}")
    else:
        print(f"   ❌ {symbol} not found")
    
    print("\n✅ Error handling examples completed!")


def example_with_data_sources():
    """
    Example 5: Using improved load_ccxt_data function
    """
    print("\n" + "=" * 70)
    print("Example 5: Using load_ccxt_data (with improvements)")
    print("=" * 70)
    
    from providers.data_sources import load_ccxt_data
    
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print(f"\n1. Loading 30 days of BTC/USDT data from Binance...")
        print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        data = load_ccxt_data(
            exchange_name='binance',
            pair='BTC/USDT',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            timeframe='1d'
        )
        
        print(f"\n   ✅ Loaded {len(data['Date'])} candles")
        print(f"\n   Last 3 candles:")
        for i in range(max(0, len(data['Date']) - 3), len(data['Date'])):
            print(f"      {data['Date'][i]}: O=${data['Open'][i]:,.2f} "
                  f"H=${data['High'][i]:,.2f} L=${data['Low'][i]:,.2f} C=${data['Close'][i]:,.2f}")
        
        print("\n✅ Data loading example completed!")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def main():
    """Main function to run examples"""
    print("\n" + "=" * 70)
    print("CCXT Best Practices Examples")
    print("Following SKILL.md guidelines")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = 'all'
    
    if mode in ['sync', 'all']:
        example_sync_basic()
    
    if mode in ['async-single', 'all']:
        asyncio.run(example_async_basic())
    
    if mode in ['async-multi', 'all']:
        asyncio.run(example_async_multiple_exchanges())
    
    if mode in ['errors', 'all']:
        example_error_handling()
    
    if mode in ['data', 'all']:
        example_with_data_sources()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\n📖 Learn more:")
    print("   - CCXT Manual: https://docs.ccxt.com/")
    print("   - Skill guide: .agent/ccxt-python/SKILL.md")
    print("   - Supported exchanges: https://github.com/ccxt/ccxt#exchanges\n")


if __name__ == '__main__':
    main()

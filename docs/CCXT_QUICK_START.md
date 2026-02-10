# CCXT Integration - Quick Start Guide

Hướng dẫn sử dụng CCXT để lấy dữ liệu cryptocurrency cho pypnf.

## Tổng quan

CCXT hỗ trợ **111+ sàn giao dịch cryptocurrency**, bao gồm:
- ✅ **REST API** - Lấy dữ liệu OHLCV (candlesticks) lịch sử
- ✅ **WebSocket API** - Real-time streaming (ccxt.pro)
- ✅ **Sync & Async** - Python sync và asyncio
- ✅ **Rate limiting** - Tự động throttle requests
- ✅ **Error handling** - Hierarchy rõ ràng (recoverable vs non-recoverable)

## Cài đặt

### CCXT Standard (REST API)
```bash
pip install ccxt
```

### Optional: Performance Enhancements
```bash
pip install orjson      # Faster JSON parsing
pip install coincurve   # Faster ECDSA signing
```

**Lưu ý:** WebSocket API (ccxt.pro) đã bao gồm trong package `ccxt`, không cần cài đặt riêng.

## Sàn giao dịch hỗ trợ

### Top exchanges:
- **Binance** - Liquidity cao, fee thấp
- **Coinbase** - US-based, regulated
- **Kraken** - EU-based, nhiều fiat pairs
- **OKX** - Derivatives, futures
- **Bybit** - Derivatives, perpetuals
- **Gate.io** - Altcoins
- **Kucoin** - Altcoins
- **Huobi** - Asia markets

Xem danh sách đầy đủ: https://github.com/ccxt/ccxt#supported-exchanges

## Cách sử dụng cơ bản

### 1. Lấy dữ liệu với pnfchart.py (đơn giản nhất)

```bash
# BTC/USDT from Binance (default)
python pnfchart.py BTC/USDT --source ccxt --exchange binance

# ETH/USDT with specific timeframe
python pnfchart.py ETH/USDT --source ccxt --exchange binance --timeframe 4h

# 30 days of data
python pnfchart.py SOL/USDT --source ccxt --exchange binance \
    --start 2024-01-01 --end 2024-01-31

# From different exchange
python pnfchart.py BTC/USD --source ccxt --exchange coinbase
```

### 2. Sử dụng trực tiếp trong Python

```python
from data_sources import load_ccxt_data
from pnfchart import PointFigureChart

# Load 30 days of BTC data
data = load_ccxt_data(
    exchange_name='binance',
    pair='BTC/USDT',
    start_date='2024-01-01',
    end_date='2024-01-31',
    timeframe='1d'
)

# Create chart
pnf = PointFigureChart(
    ts=data,
    method='hl',
    reversal=3,
    boxsize=100,
    title='BTC/USDT'
)

print(pnf)
```

## Timeframes hỗ trợ

Các timeframe phổ biến (tùy exchange):

| Timeframe | Mô tả | Ví dụ sử dụng |
|-----------|-------|---------------|
| `1m` | 1 minute | Scalping, intraday |
| `5m` | 5 minutes | Short-term trading |
| `15m` | 15 minutes | Short-term trading |
| `1h` | 1 hour | Day trading |
| `4h` | 4 hours | Swing trading |
| `1d` | 1 day | Position trading (default) |
| `1w` | 1 week | Long-term analysis |

**Kiểm tra timeframes của exchange:**
```python
from data_sources import get_exchange_timeframes
print(get_exchange_timeframes('binance'))
# ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
```

## Symbol formats

### Format chuẩn: `BASE/QUOTE`

- **Spot:** `BTC/USDT`, `ETH/USD`, `ADA/BTC`
- **Futures:** `BTC/USDT:USDT` (perpetual)
- **Inverse futures:** `BTC/USD:BTC`

### Kiểm tra symbols của exchange:

```python
from data_sources import get_exchange_symbols
symbols = get_exchange_symbols('binance')
print(f"Total symbols: {len(symbols)}")
print("Sample:", symbols[:10])
```

## Ví dụ nâng cao

### Ví dụ 1: So sánh nhiều exchanges

```bash
# Compare BTC price across exchanges
python pnfchart.py BTC/USDT --source ccxt --exchange binance
python pnfchart.py BTC/USDT --source ccxt --exchange kraken
python pnfchart.py BTC/USD --source ccxt --exchange coinbase
```

### Ví dụ 2: Nhiều timeframes

```bash
# Daily chart
python pnfchart.py ETH/USDT --source ccxt --timeframe 1d

# 4-hour chart for more detail
python pnfchart.py ETH/USDT --source ccxt --timeframe 4h

# 1-hour for intraday
python pnfchart.py ETH/USDT --source ccxt --timeframe 1h
```

### Ví dụ 3: Altcoins

```bash
# Popular altcoins
python pnfchart.py SOL/USDT --source ccxt --exchange binance
python pnfchart.py ADA/USDT --source ccxt --exchange binance
python pnfchart.py DOGE/USDT --source ccxt --exchange binance
python pnfchart.py MATIC/USDT --source ccxt --exchange binance
```

### Ví dụ 4: Custom parameters

```bash
python pnfchart.py BTC/USDT \
    --source ccxt \
    --exchange binance \
    --start 2024-01-01 \
    --end 2024-12-31 \
    --timeframe 1d \
    --method hl \
    --reversal 3 \
    --boxsize 500 \
    --scaling abs
```

## Best Practices (theo SKILL.md)

### ✅ DO: Những điều nên làm

1. **Dùng rate limiting tự động:**
   ```python
   exchange = ccxt.binance({'enableRateLimit': True})
   ```

2. **Load markets trước khi fetch:**
   ```python
   exchange.load_markets()
   if 'BTC/USDT' in exchange.markets:
       ticker = exchange.fetch_ticker('BTC/USDT')
   ```

3. **Error handling đúng:**
   ```python
   try:
       data = exchange.fetch_ohlcv('BTC/USDT', '1d')
   except ccxt.NetworkError as e:
       # Recoverable - retry
       print(f"Network error: {e}")
   except ccxt.ExchangeError as e:
       # Non-recoverable - don't retry
       print(f"Exchange error: {e}")
   ```

4. **Close async connections:**
   ```python
   import ccxt.async_support as ccxt
   
   exchange = ccxt.binance()
   try:
       await exchange.fetch_ticker('BTC/USDT')
   finally:
       await exchange.close()  # Important!
   ```

### ❌ DON'T: Những điều tránh

1. **Không disable rate limiting:**
   ```python
   # ❌ Bad
   exchange = ccxt.binance()
   
   # ✅ Good
   exchange = ccxt.binance({'enableRateLimit': True})
   ```

2. **Không bỏ qua error handling:**
   ```python
   # ❌ Bad
   data = exchange.fetch_ohlcv('BTC/USDT', '1d')
   
   # ✅ Good
   try:
       data = exchange.fetch_ohlcv('BTC/USDT', '1d')
   except ccxt.NetworkError:
       # Handle retry
   except ccxt.ExchangeError:
       # Handle failure
   ```

3. **Không quên close async:**
   ```python
   # ❌ Bad - resource leak
   exchange = ccxt_async.binance()
   await exchange.fetch_ticker('BTC/USDT')
   # Forgot to close!
   
   # ✅ Good
   exchange = ccxt_async.binance()
   try:
       await exchange.fetch_ticker('BTC/USDT')
   finally:
       await exchange.close()
   ```

## Error Handling

Hierarchy của CCXT errors:

```
BaseError
├─ NetworkError (recoverable - có thể retry)
│  ├─ RequestTimeout
│  ├─ ExchangeNotAvailable
│  ├─ RateLimitExceeded
│  └─ DDoSProtection
└─ ExchangeError (non-recoverable - KHÔNG retry)
   ├─ AuthenticationError
   ├─ InsufficientFunds
   ├─ InvalidOrder
   ├─ BadSymbol
   └─ NotSupported
```

### Xử lý lỗi phổ biến:

#### 1. RateLimitExceeded
```bash
⚠️  Rate limit exceeded. Waiting before retry...
```
**Giải pháp:**
- Đợi vài giây rồi thử lại
- Dùng `enableRateLimit: True`
- Tăng timeframe (1m → 1h)

#### 2. BadSymbol / Invalid pair
```bash
❌ Symbol 'BTC/USD' not found on binance.
Similar symbols: BTC/USDT, BTC/BUSD, BTC/EUR
```
**Giải pháp:**
- Kiểm tra symbol format: `BASE/QUOTE`
- Binance dùng `USDT` không phải `USD`
- Dùng `get_exchange_symbols('binance')` để xem symbols

#### 3. NetworkError
```bash
❌ Network error: Connection timeout
```
**Giải pháp:**
- Kiểm tra internet connection
- Thử lại sau vài giây
- Có thể exchange đang maintenance

#### 4. ExchangeNotAvailable
```bash
❌ Exchange not available: The exchange may be under maintenance.
```
**Giải pháp:**
- Đợi exchange khôi phục
- Thử exchange khác
- Check exchange status page

## Sync vs Async

### Khi nào dùng Sync (hiện tại trong pypnf):
- ✅ Scripts đơn giản
- ✅ Single exchange operations
- ✅ Jupyter notebooks
- ✅ Testing/debugging

### Khi nào dùng Async:
- Multiple exchanges concurrently
- High-performance bots
- WebSocket connections (bắt buộc)
- Monitoring nhiều symbols

### Example Async (nếu cần):

```python
import asyncio
import ccxt.async_support as ccxt

async def fetch_multiple():
    exchanges = [
        ccxt.binance({'enableRateLimit': True}),
        ccxt.coinbase({'enableRateLimit': True}),
    ]
    
    try:
        tasks = [ex.fetch_ticker('BTC/USDT') for ex in exchanges]
        results = await asyncio.gather(*tasks)
        return results
    finally:
        for ex in exchanges:
            await ex.close()

# Run
asyncio.run(fetch_multiple())
```

## Testing & Debugging

### 1. Kiểm tra exchange capabilities:
```python
import ccxt
exchange = ccxt.binance()
print(exchange.has)
# {
#   'fetchTicker': True,
#   'fetchOHLCV': True,
#   'fetchMyTrades': False,  # Requires API key
#   ...
# }
```

### 2. Test connection:
```python
try:
    exchange.load_markets()
    print(f"✅ Connected to {exchange.name}")
    print(f"   Markets: {len(exchange.markets)}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### 3. Verbose logging:
```python
exchange = ccxt.binance({
    'enableRateLimit': True,
    'verbose': True  # Show all HTTP requests
})
```

### 4. Chạy example scripts:
```bash
# Basic sync example
python example_ccxt_usage.py sync

# Async single exchange
python example_ccxt_usage.py async-single

# Multiple exchanges
python example_ccxt_usage.py async-multi

# Error handling demo
python example_ccxt_usage.py errors

# All examples
python example_ccxt_usage.py all
```

## Improvements trong pypnf

Code CCXT trong pypnf đã được cải thiện theo SKILL.md:

### ✅ Đã implement:
1. ✅ `enableRateLimit: True` by default
2. ✅ Load markets trước khi fetch
3. ✅ Validate symbol exists
4. ✅ Validate timeframe support
5. ✅ Error hierarchy đúng (NetworkError vs ExchangeError)
6. ✅ Retry logic cho network errors (max 3 retries)
7. ✅ Exponential backoff
8. ✅ Helpful error messages
9. ✅ Progress indicator
10. ✅ Timeout configuration

### 📋 TODO (nếu cần):
- [ ] Async variant của `load_ccxt_data`
- [ ] WebSocket support (ccxt.pro) cho real-time
- [ ] Caching market data
- [ ] Batch symbol fetching
- [ ] Volume data inclusion

## Troubleshooting

### Issue: "Exchange not found"
```bash
❌ Exchange 'binnance' not found
```
**Fix:** Sửa typo: `binance` (không phải `binnance`)

### Issue: "Symbol not found"
```bash
❌ Symbol 'BTCUSD' not found
```
**Fix:** Dùng format `BTC/USDT` với dấu `/`

### Issue: "No data returned"
```bash
❌ No data found for BTC/USDT
```
**Fix:**
- Kiểm tra date range (không quá xa trong quá khứ)
- Exchange có thể không có data cho timeframe đó
- Thử timeframe khác (1d thường available nhất)

### Issue: SSL errors
```bash
❌ SSL: CERTIFICATE_VERIFY_FAILED
```
**Fix:**
```bash
pip install --upgrade certifi
```

## Tài liệu tham khảo

- **SKILL Guide:** `.agent/ccxt-python/SKILL.md` (chi tiết đầy đủ)
- **CCXT Manual:** https://docs.ccxt.com/
- **Supported Exchanges:** https://github.com/ccxt/ccxt#exchanges
- **Example Script:** `example_ccxt_usage.py`
- **Code:** `data_sources.py` (function `load_ccxt_data`)

## Tips & Tricks

### 1. Tìm symbol nhanh:
```python
from data_sources import get_exchange_symbols
symbols = get_exchange_symbols('binance')
btc_pairs = [s for s in symbols if 'BTC/' in s]
print(btc_pairs[:10])
```

### 2. So sánh giá:
```bash
for ex in binance coinbase kraken; do
    echo "=== $ex ==="
    python -c "import ccxt; e=ccxt.$ex(); e.load_markets(); print(e.fetch_ticker('BTC/USDT')['last'] if 'BTC/USDT' in e.markets else 'N/A')"
done
```

### 3. Batch charts:
```bash
for pair in BTC/USDT ETH/USDT SOL/USDT; do
    python pnfchart.py $pair --source ccxt --exchange binance
done
```

---

**🎯 Quick Start:**
```bash
# Single command to get started
python pnfchart.py BTC/USDT --source ccxt --exchange binance

# With custom parameters
python pnfchart.py BTC/USDT --source ccxt --exchange binance \
    --timeframe 4h --method hl --reversal 3
```

Enjoy trading! 📈🚀

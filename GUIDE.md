# Point & Figure Chart - Hướng Dẫn Sử Dụng

## Giới thiệu

Script `pnfchart.py` cho phép bạn tạo biểu đồ Point & Figure từ dữ liệu cổ phiếu (Yahoo Finance) hoặc tiền điện tử/crypto (CCXT exchanges) với nhiều tùy chọn linh hoạt thông qua command line.

**Tính năng chính:**
- Phân tích dữ liệu cổ phiếu từ Yahoo Finance
- Phân tích dữ liệu crypto từ 100+ sàn giao dịch (Binance, Kraken, Coinbase, ...)
- Động tính phép vị tẤp Point & Figure với nhiều tùy chọn scaling
- Hiển thị trendlines, breakouts, và các mô hình giá

## Cài đặt

```bash
pip install ccxt yfinance pandas
```

**Các gói đàu tiên:**
- `ccxt`: Hỗ trợ 100+ sàn giao dịch crypto
- `yfinance`: Lấy dữ liệu cổ phiếu Yahoo Finance
- `pandas`: Xử lý dữ liệu

## Cách Sử Dụng Cơ Bản

### 1. Chạy với mã cổ phiếu mặc định (AMD)

```bash
python pnfchart.py
```

### 2. Chạy với mã cổ phiếu bất kỳ

```bash
python pnfchart.py AAPL
python pnfchart.py MSFT
python pnfchart.py TSLA
python pnfchart.py NVDA
python pnfchart.py VFS
```

### 3. Xem tất cả các tùy chọn

```bash
python pnfchart.py --help
```

## Các Tham Số Chi Tiết

### Tham số vị trí (Positional Arguments)

| Tham số | Mô tả | Mặc định |
|---------|-------|----------|
| `symbol` | Stock/Crypto symbol (ví dụ: AMD, BTC/USDT) | AMD |

### Các tùy chọn (Options)

| Tham số | Mô tả | Giá trị | Mặc định |
|---------|-------|---------|----------|
| `--source` | Nguồn dữ liệu | yfinance, ccxt | yfinance |
| `--start` | Ngày bắt đầu | YYYY-MM-DD | 2010-01-01 |
| `--end` | Ngày kết thúc | YYYY-MM-DD | Hôm nay (today) |
| `--exchange` | Sàn giao dịch CCXT | binance, kraken, coinbase, ... | binance |
| `--timeframe` | Khung thời gian (CCXT) | 1m, 5m, 15m, 1h, 4h, 1d, 1w | 1d |
| `--method` | Phương pháp vẽ chart | cl, h/l, l/h, hlc, ohlc | h/l |
| `--reversal` | Số box để đảo chiều | Số nguyên | 3 |
| `--boxsize` | Kích thước box | Số thực | 1 |
| `--scaling` | Phương pháp scaling | abs, atr, cla, log | cla |
| `--save` | Lưu chart vào file HTML | Flag | False |
| `--show` | Hiển thị chart với matplotlib | Flag | False |
| `--no-trendlines` | Bỏ qua tính toán trendlines | Flag | False |
| `--no-breakouts` | Bỏ qua tính toán breakouts | Flag | False |
| `--no-signals` | Bỏ qua tính toán signals/patterns | Flag | False |
| `--columns` | Số cột hiển thị trong console | Số nguyên | 30 (dùng 0 để hiển thị tất cả) |

## Chi Tiết Các Tham Số

### METHOD (Phương pháp)

- **cl** (Close): Chỉ dùng giá đóng cửa
- **h/l** (High/Low): Dùng giá cao/thấp (mặc định)
- **l/h** (Low/High): Dùng giá thấp/cao
- **hlc** (High/Low/Close): Kết hợp giá cao/thấp/đóng cửa
- **ohlc** (Open/High/Low/Close): Dùng đầy đủ OHLC

### REVERSAL (Đảo chiều)

Số lượng box tối thiểu cần thiết để chart đảo chiều xu hướng.

- `2`: Đảo chiều nhanh, nhiều tín hiệu
- `3`: Cân bằng (mặc định)
- `4+`: Đảo chiều chậm, lọc nhiễu tốt hơn

### SOURCE (Nguồn dữ liệu)

#### 1. **yfinance** - Stock Data (Mặc định)

Lấy dữ liệu cổ phiếu từ Yahoo Finance.

```bash
# Cố phiếu US
python pnfchart.py AAPL --source yfinance
python pnfchart.py MSFT --source yfinance
python pnfchart.py TSLA --source yfinance

# Cố phiếu quốc tế
python pnfchart.py 0700.HK --source yfinance  # Alibaba
python pnfchart.py ^HSI --source yfinance     # Hang Seng Index
python pnfchart.py ^GSPC --source yfinance    # S&P 500
```

#### 1. **ccxt** - Cryptocurrency Data

Lấy dữ liệu crypto từ nhiều sàn giao dịch. Ở đây:
- Pair: Dùng định dạng `BTC/USDT`, `ETH/USD`, vàv...
- Exchange: binance, kraken, coinbase, huobi, bybit, vàv...
- Timeframe: 1m, 5m, 15m, 1h, 4h, 1d, 1w

```bash
# Bitcoin từ Binance
python pnfchart.py BTC/USDT --source ccxt --exchange binance

# Ethereum từ Kraken
python pnfchart.py ETH/USD --source ccxt --exchange kraken

# Các timeframe khác nhau
python pnfchart.py BTC/USDT --source ccxt --exchange binance --timeframe 1h
python pnfchart.py BTC/USDT --source ccxt --exchange binance --timeframe 4h
python pnfchart.py BTC/USDT --source ccxt --exchange binance --timeframe 1w

# Với kồng thời gian cụ thể
python pnfchart.py BTC/USDT --source ccxt --exchange binance --start 2025-08-01 --end 2025-12-31
```

### SCALING (Tỷ lệ)

#### 1. **abs** - Absolute (Tuyệt đối)
```bash
python pnfchart.py AAPL --scaling abs --boxsize 5
```
- Mỗi box có kích thước cố định (ví dụ: $5)
- Phù hợp với cổ phiếu giá ổn định

#### 2. **atr** - Average True Range
```bash
python pnfchart.py AAPL --scaling atr --boxsize 14
```
- Boxsize = số kỳ để tính ATR (ví dụ: 14 ngày)
- Tự động điều chỉnh theo biến động thị trường
- Có thể dùng `total` để tính trên toàn bộ dữ liệu

#### 3. **cla** - Classic (Truyền thống)
```bash
python pnfchart.py AAPL --scaling cla --boxsize 1
```
- Phương pháp Point & Figure cổ điển
- Boxsize là hệ số nhân: 0.02, 0.05, 0.1, 0.25, 1/3, 0.5, 1, 2
- Tự động điều chỉnh theo mức giá

#### 4. **log** - Logarithmic
```bash
python pnfchart.py AAPL --scaling log --boxsize 1
```
- Boxsize là % (ví dụ: 1 = 1%)
- Phù hợp với cổ phiếu có biên độ giá rộng
- Giá trị tối thiểu: 0.01%

### COLUMNS (Số cột hiển thị)

Điều chỉnh số cột hiển thị trong console để xem nhiều hoặc ít dữ liệu hơn.

```bash
# Hiển thị 50 cột gần nhất
python pnfchart.py NVDA --columns 50

# Hiển thị 100 cột gần nhất
python pnfchart.py AAPL --columns 100

# Hiển thị TẤT CẢ các cột (có thể rất rộng)
python pnfchart.py MSFT --columns 0
```

**Lưu ý:**
- Mặc định: 30 cột (phù hợp với console thông thường)
- Dùng `--columns 0` để hiển thị toàn bộ chart (hữu ích khi xuất ra file)
- Số cột lớn hơn có thể bị wrap lines trên màn hình nhỏ
- Chart luôn hiển thị các cột gần nhất (rightmost columns)

## Ví Dụ Thực Tế

### Ví dụ 1: Phân tích AMD với cài đặt mặc định

```bash
python pnfchart.py AMD
```

### Ví dụ 2: Phân tích AAPL với method đóng cửa

```bash
python pnfchart.py AAPL --method cl --reversal 2
```

### Ví dụ 3: Phân tích TSLA từ 2020 với log scaling

```bash
python pnfchart.py TSLA --start 2020-01-01 --scaling log --boxsize 1
```

### Ví dụ 4: Phân tích nhanh không cần patterns

```bash
python pnfchart.py NVDA --no-signals --no-breakouts
```

### Ví dụ 5: Lưu chart và hiển thị

```bash
python pnfchart.py MSFT --save --show
```

### Ví dụ 6: Phân tích chi tiết với nhiều tùy chọn

```bash
python pnfchart.py AMD \
  --start 2015-01-01 \
  --method h/l \
  --reversal 3 \
  --boxsize 2 \
  --scaling cla \
  --save
```

### Ví dụ 7: So sánh các scaling khác nhau

```bash
# Absolute scaling
python pnfchart.py AAPL --scaling abs --boxsize 10

# Log scaling
python pnfchart.py AAPL --scaling log --boxsize 2

# Classic scaling
python pnfchart.py AAPL --scaling cla --boxsize 1
```

### Ví dụ 8: Phân tích Cryptocurrency - Bitcoin từ Binance

```bash
# Bitcoin 1 ngày (default)
python pnfchart.py BTC/USDT --source ccxt --exchange binance --no-signals --no-breakouts

# Bitcoin 4 giờ
python pnfchart.py BTC/USDT --source ccxt --exchange binance --timeframe 4h --columns 50

# Bitcoin với trendlines
python pnfchart.py BTC/USDT --source ccxt --exchange binance --start 2025-06-01 --end 2025-12-31
```

### Ví dụ 9: Phân tích altcoins từ các sàn khác nhau

```bash
# Ethereum từ Kraken
python pnfchart.py ETH/USD --source ccxt --exchange kraken --timeframe 1h

# XRP từ Binance  
python pnfchart.py XRP/USDT --source ccxt --exchange binance --start 2025-01-01

# Litecoin từ Coinbase
python pnfchart.py LTC/USD --source ccxt --exchange coinbase --timeframe 1d
```

## Hiểu Output của Chart

### 1. Chart Cơ Bản
```
Point & Figure (cla|h/l) 2@50 x 3 | AAPL
```
- `cla`: Classic scaling
- `h/l`: High/Low method
- `2@50`: Boxsize 2 tại scale 50
- `x 3`: Reversal = 3

### 2. Ký Hiệu Trên Chart

- `X`: Giá tăng
- `O`: Giá giảm
- `.`: Box trống
- `*`: Trendline (chỉ hiện trên box trống)

### 3. Thông Tin Trendlines

```
External Trendlines (4 found):
  1. bullish support        | length:  48 | col:   1 | price: 5.7
  2. bearish resistance     | length:  12 | col:   8 | price: 0.6
```

- **Type**: bullish support / bearish resistance
- **Length**: Độ dài (số cột)
- **Column**: Vị trí bắt đầu
- **Price**: Mức giá

### 4. Thông Tin Breakouts

```
Breakouts in displayed range (18 found):
  1. Bullish  reversal     | col:  22 | price: 26 | hits:  2
  2. Bearish  continuation | col:  43 | price: 124 | hits:  3
```

- **Trend**: Bullish / Bearish
- **Type**: reversal, resistance, continuation, fulcrum
- **Column**: Vị trí xảy ra breakout
- **Price**: Mức giá breakout
- **Hits**: Số lần test trước khi breakout

### 5. Signals/Patterns

Các mô hình được phát hiện:
- Double Top Breakout
- Triple Top Breakout
- Bullish/Bearish Catapult
- Triangle Breakout
- High/Low Poles
- Bull/Bear Traps
- Và nhiều mô hình khác...

## Tips & Best Practices

### 1. Chọn Scaling phù hợp

- **Cổ phiếu giá thấp (<$20)**: Dùng `abs` hoặc `cla`
- **Cổ phiếu giá cao (>$100)**: Dùng `log` hoặc `cla`
- **Cổ phiếu biến động cao**: Dùng `atr`
- **Phân tích chung**: Dùng `cla` (mặc định)

### 2. Chọn Reversal phù hợp

- **Ngắn hạn/Day trading**: reversal = 2
- **Trung hạn/Swing trading**: reversal = 3 (mặc định)
- **Dài hạn/Position trading**: reversal = 4-5

### 3. Tối ưu hiệu năng

Nếu chỉ cần xem chart nhanh, bỏ qua các tính toán phức tạp:

```bash
python pnfchart.py AAPL --no-signals --no-breakouts
```

### 4. Lưu kết quả

Để xem chi tiết và tương tác, lưu ra file HTML:

```bash
python pnfchart.py AAPL --save
# Mở file AAPL_pnf_chart.html trong browser
```

### 5. Phân tích Cryptocurrency (CCXT)

**Các sàn giao dịch hỗ trợ (phổ biến):**
- `binance`: Sàn lớn nhất (hầu hết cặp)
- `kraken`: Sàn uy tín (Bitcoin, Ethereum, altcoins)
- `coinbase`: Sàn US (chủ yếu BTC, ETH, LTC)
- `huobi`: Sàn Trung Quốc
- `bybit`: Sàn futures
- `kucoin`, `bitfinex`, `gemini`, ...

**Chọn timeframe phù hợp:**
- `1m`, `5m`, `15m`: Scalping/intraday
- `1h`, `4h`: Day trading
- `1d`: Swing trading (mặc định)
- `1w`: Position trading

**Cú pháp pair:**
- Binance: `BTC/USDT`, `ETH/BUSD`, `XRP/USDT`
- Kraken: `BTC/USD`, `ETH/USD`, `XRP/USD`
- Coinbase: `BTC/USD`, `ETH/USD`, `LTC/USD`

**Ví dụ:**
```bash
# Giao dịch 4 giờ
python pnfchart.py BTC/USDT --source ccxt --exchange binance --timeframe 4h

# Giao dịch 1 giờ với cảnh báo trendlines
python pnfchart.py ETH/USDT --source ccxt --exchange binance --timeframe 1h --columns 30

# Phân tích dài hạn
python pnfchart.py BTC/USDT --source ccxt --exchange binance --start 2023-01-01
```

## Xử Lý Lỗi Thường Gặp

### 1. Lỗi "No data found"

```bash
# Kiểm tra mã cổ phiếu có đúng không
python pnfchart.py AAPL  # Đúng
python pnfchart.py Apple # Sai
```

### 2. Lỗi "Signals calculation encountered an issue"

Một số dữ liệu có thể gây lỗi khi tính toán patterns. Sử dụng:

```bash
python pnfchart.py STOCK --no-signals
```

### 3. Chart quá dài

Giảm khoảng thời gian hoặc tăng reversal:

```bash
python pnfchart.py AAPL --start 2023-01-01
# Hoặc
python pnfchart.py AAPL --reversal 5
```

### 4. Lỗi CCXT - "No symbols found" hoặc "Pair not available"

Kiểm tra tên pair và sàn giao dịch:

```bash
# Sai: python pnfchart.py BTCUSDT --source ccxt  (Thiếu /)
# Đúng:
python pnfchart.py BTC/USDT --source ccxt --exchange binance

# Kiểm tra pair trên sàn khác
python pnfchart.py BTC/USD --source ccxt --exchange kraken
```

### 5. Lỗi CCXT - "Rate limit exceeded"

Một số sàn giới hạn tốc độ request. Script sẽ tự pause, nhưng bạn có thể:

```bash
# Thử lại với dữ liệu trong ngày
python pnfchart.py BTC/USDT --source ccxt --exchange binance --start 2025-12-01
```

### 6. Lỗi CCXT - "Network error"

Kiểm tra kết nối internet hoặc sàn có khả dụng không:

```bash
# Thử sàn khác
python pnfchart.py BTC/USDT --source ccxt --exchange kraken
```

## Tích Hợp Vào Workflow

### Script tự động

```bash
#!/bin/bash
# Tạo chart cho nhiều mã cổ phiếu
for symbol in AAPL MSFT GOOGL TSLA NVDA; do
    python pnfchart.py $symbol --save --no-signals
    echo "✓ Completed $symbol"
done
```

### Cron job (Linux/Mac)

```bash
# Chạy hàng ngày lúc 5:00 PM
0 17 * * * cd /path/to/pypnf && python pnfchart.py AMD --save
```

## Tài Liệu Tham Khảo

- **README.md**: Tài liệu chính của thư viện pypnf
- **Documentation**: https://github.com/swaschke/pypnf
- **Sách tham khảo**:
  - The Complete Guide to Point-and-Figure Charting (Weber, Zieg, 2003)
  - The Definitive Guide to Point and Figure (du Plessis, 2012)

## Liên Hệ & Hỗ Trợ

- GitHub Issues: https://github.com/fivethreeo/pypnf/issues
- Original Project: https://github.com/swaschke/pypnf

---

**Version**: 1.0  
**Last Updated**: February 2026

# Point & Figure Chart - Hướng Dẫn Sử Dụng

## Giới thiệu

Script `example_yfinance.py` cho phép bạn tạo biểu đồ Point & Figure từ dữ liệu cổ phiếu trên Yahoo Finance với nhiều tùy chọn linh hoạt thông qua command line.

## Cài đặt

```bash
pip install pypnf yfinance pandas
```

## Cách Sử Dụng Cơ Bản

### 1. Chạy với mã cổ phiếu mặc định (AMD)

```bash
python example_yfinance.py
```

### 2. Chạy với mã cổ phiếu bất kỳ

```bash
python example_yfinance.py AAPL
python example_yfinance.py MSFT
python example_yfinance.py TSLA
python example_yfinance.py NVDA
python example_yfinance.py VFS
```

### 3. Xem tất cả các tùy chọn

```bash
python example_yfinance.py --help
```

## Các Tham Số Chi Tiết

### Tham số vị trí (Positional Arguments)

| Tham số | Mô tả | Mặc định |
|---------|-------|----------|
| `symbol` | Mã cổ phiếu (ticker symbol) | AMD |

### Các tùy chọn (Options)

| Tham số | Mô tả | Giá trị | Mặc định |
|---------|-------|---------|----------|
| `--start` | Ngày bắt đầu | YYYY-MM-DD | 2010-01-01 |
| `--end` | Ngày kết thúc | YYYY-MM-DD | Hôm nay (today) |
| `--method` | Phương pháp vẽ chart | cl, h/l, l/h, hlc, ohlc | h/l |
| `--reversal` | Số box để đảo chiều | Số nguyên | 3 |
| `--boxsize` | Kích thước box | Số thực | 2 |
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

### SCALING (Tỷ lệ)

#### 1. **abs** - Absolute (Tuyệt đối)
```bash
python example_yfinance.py AAPL --scaling abs --boxsize 5
```
- Mỗi box có kích thước cố định (ví dụ: $5)
- Phù hợp với cổ phiếu giá ổn định

#### 2. **atr** - Average True Range
```bash
python example_yfinance.py AAPL --scaling atr --boxsize 14
```
- Boxsize = số kỳ để tính ATR (ví dụ: 14 ngày)
- Tự động điều chỉnh theo biến động thị trường
- Có thể dùng `total` để tính trên toàn bộ dữ liệu

#### 3. **cla** - Classic (Truyền thống)
```bash
python example_yfinance.py AAPL --scaling cla --boxsize 1
```
- Phương pháp Point & Figure cổ điển
- Boxsize là hệ số nhân: 0.02, 0.05, 0.1, 0.25, 1/3, 0.5, 1, 2
- Tự động điều chỉnh theo mức giá

#### 4. **log** - Logarithmic
```bash
python example_yfinance.py AAPL --scaling log --boxsize 1
```
- Boxsize là % (ví dụ: 1 = 1%)
- Phù hợp với cổ phiếu có biên độ giá rộng
- Giá trị tối thiểu: 0.01%

### COLUMNS (Số cột hiển thị)

Điều chỉnh số cột hiển thị trong console để xem nhiều hoặc ít dữ liệu hơn.

```bash
# Hiển thị 50 cột gần nhất
python example_yfinance.py NVDA --columns 50

# Hiển thị 100 cột gần nhất
python example_yfinance.py AAPL --columns 100

# Hiển thị TẤT CẢ các cột (có thể rất rộng)
python example_yfinance.py MSFT --columns 0
```

**Lưu ý:**
- Mặc định: 30 cột (phù hợp với console thông thường)
- Dùng `--columns 0` để hiển thị toàn bộ chart (hữu ích khi xuất ra file)
- Số cột lớn hơn có thể bị wrap lines trên màn hình nhỏ
- Chart luôn hiển thị các cột gần nhất (rightmost columns)

## Ví Dụ Thực Tế

### Ví dụ 1: Phân tích AMD với cài đặt mặc định

```bash
python example_yfinance.py AMD
```

### Ví dụ 2: Phân tích AAPL với method đóng cửa

```bash
python example_yfinance.py AAPL --method cl --reversal 2
```

### Ví dụ 3: Phân tích TSLA từ 2020 với log scaling

```bash
python example_yfinance.py TSLA --start 2020-01-01 --scaling log --boxsize 1
```

### Ví dụ 4: Phân tích nhanh không cần patterns

```bash
python example_yfinance.py NVDA --no-signals --no-breakouts
```

### Ví dụ 5: Lưu chart và hiển thị

```bash
python example_yfinance.py MSFT --save --show
```

### Ví dụ 6: Phân tích chi tiết với nhiều tùy chọn

```bash
python example_yfinance.py AMD \
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
python example_yfinance.py AAPL --scaling abs --boxsize 10

# Log scaling
python example_yfinance.py AAPL --scaling log --boxsize 2

# Classic scaling
python example_yfinance.py AAPL --scaling cla --boxsize 1
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
python example_yfinance.py AAPL --no-signals --no-breakouts
```

### 4. Lưu kết quả

Để xem chi tiết và tương tác, lưu ra file HTML:

```bash
python example_yfinance.py AAPL --save
# Mở file AAPL_pnf_chart.html trong browser
```

## Xử Lý Lỗi Thường Gặp

### 1. Lỗi "No data found"

```bash
# Kiểm tra mã cổ phiếu có đúng không
python example_yfinance.py AAPL  # Đúng
python example_yfinance.py Apple # Sai
```

### 2. Lỗi "Signals calculation encountered an issue"

Một số dữ liệu có thể gây lỗi khi tính toán patterns. Sử dụng:

```bash
python example_yfinance.py STOCK --no-signals
```

### 3. Chart quá dài

Giảm khoảng thời gian hoặc tăng reversal:

```bash
python example_yfinance.py AAPL --start 2023-01-01
# Hoặc
python example_yfinance.py AAPL --reversal 5
```

## Tích Hợp Vào Workflow

### Script tự động

```bash
#!/bin/bash
# Tạo chart cho nhiều mã cổ phiếu
for symbol in AAPL MSFT GOOGL TSLA NVDA; do
    python example_yfinance.py $symbol --save --no-signals
    echo "✓ Completed $symbol"
done
```

### Cron job (Linux/Mac)

```bash
# Chạy hàng ngày lúc 5:00 PM
0 17 * * * cd /path/to/pypnf && python example_yfinance.py AMD --save
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

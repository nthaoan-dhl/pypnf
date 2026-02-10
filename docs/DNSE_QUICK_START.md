# DNSE Integration - Quick Start Guide

Hướng dẫn tích hợp DNSE Lightspeed để lấy dữ liệu OHLC cho thị trường Việt Nam.

## Tổng quan

DNSE provider hỗ trợ:
- ✅ Lấy snapshot OHLC qua HTTP API
- ✅ Kết hợp với lịch sử từ vnstock (tùy chọn)
- ✅ Cấu hình linh hoạt qua biến môi trường
- ❌ Không hỗ trợ real-time streaming
- ⚠️ Volume chưa được implement (chỉ OHLC, chưa có V)

## Cài đặt

### 1. Cài đặt vnstock (tùy chọn, để lấy dữ liệu lịch sử)

```bash
pip install vnstock
```

### 2. Cấu hình biến môi trường

#### Cách 1: Sử dụng DNSE_SNAPSHOT_URL (đơn giản nhất)

```bash
export DNSE_SNAPSHOT_URL="https://your-dnse-api.com/snapshot?symbol={symbol}"
export DNSE_API_KEY="your_api_key_here"  # Tùy chọn nếu cần authentication
```

#### Cách 2: Sử dụng BASE_URL + ENDPOINT (linh hoạt hơn)

```bash
export DNSE_BASE_URL="https://your-dnse-api.com"
export DNSE_SNAPSHOT_ENDPOINT="/api/v1/snapshot"
export DNSE_SYMBOL_PARAM="symbol"  # Mặc định là 'symbol'
export DNSE_API_KEY="your_api_key_here"  # Tùy chọn
```

#### Các biến môi trường khác

```bash
# Tùy chọn nâng cao
export DNSE_TIMEOUT="10"                    # Timeout request (giây)
export DNSE_MARKET_PARAM="market"           # Tên param cho market
export DNSE_TIMEFRAME_PARAM="timeframe"    # Tên param cho timeframe
export DNSE_PROVIDER="dnse_provider"        # Module provider tùy chỉnh
```

## Cách sử dụng

### 1. Chỉ lấy snapshot DNSE (không lịch sử)

Lấy giá trị OHLC hiện tại từ DNSE:

```bash
python pnfchart.py FPT --source dnse --dnse-no-history
```

### 2. Kết hợp lịch sử vnstock + snapshot DNSE (mặc định)

Lấy dữ liệu lịch sử từ vnstock, sau đó thêm snapshot DNSE nếu mới hơn:

```bash
python pnfchart.py FPT --source dnse --start 2024-01-01 --end 2025-02-09
```

### 3. Với timeframe cụ thể

```bash
python pnfchart.py VNM --source dnse --timeframe 1m --dnse-no-history
```

### 4. Tùy chỉnh provider module

Nếu bạn có custom provider:

```bash
python pnfchart.py HPG --source dnse --dnse-provider my_custom_provider
```

## Cấu trúc dữ liệu DNSE Response

Provider mong đợi response JSON theo một trong các format sau:

### Format 1: Direct object
```json
{
  "close": 65.5,
  "open": 64.0,
  "high": 66.0,
  "low": 63.5,
  "timestamp": 1707494400000
}
```

### Format 2: Wrapped in 'data'
```json
{
  "data": {
    "close": 65.5,
    "open": 64.0,
    "high": 66.0,
    "low": 63.5,
    "tradingDate": "2024-02-09"
  }
}
```

### Format 3: Wrapped in 'result'
```json
{
  "result": {
    "lastPrice": 65.5,
    "o": 64.0,
    "h": 66.0,
    "l": 63.5,
    "time": 1707494400000
  }
}
```

### Format 4: Array
```json
[
  {
    "c": 65.5,
    "o": 64.0,
    "h": 66.0,
    "l": 63.5,
    "t": 1707494400000
  }
]
```

## Field Mapping

Provider tự động nhận diện các field sau:

| Mục đích | Các tên field hỗ trợ |
|----------|----------------------|
| **Close** | `close`, `c`, `last`, `price`, `lastPrice` |
| **Open** | `open`, `o` (fallback: close) |
| **High** | `high`, `h` (fallback: close) |
| **Low** | `low`, `l` (fallback: close) |
| **Timestamp** | `timestamp`, `time`, `t`, `tradingDate`, `date` |

## Tùy chỉnh Provider

Để tạo custom provider, tạo file `my_dnse_provider.py`:

```python
import json
import urllib.request
from datetime import datetime

def fetch_snapshot(symbol, timeframe=None, market=None, **kwargs):
    """
    Fetch snapshot OHLC data.
    
    Must return dict with structure:
    {
        'Date': ['2024-02-09'],
        'Open': [64.0],
        'High': [66.0],
        'Low': [63.5],
        'Close': [65.5]
    }
    """
    # Your custom logic here
    url = f"https://your-api.com/snapshot?symbol={symbol}"
    
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())
    
    return {
        'Date': [datetime.now().strftime('%Y-%m-%d')],
        'Open': [float(data['open'])],
        'High': [float(data['high'])],
        'Low': [float(data['low'])],
        'Close': [float(data['close'])]
    }
```

Sau đó sử dụng:

```bash
python pnfchart.py FPT --source dnse --dnse-provider my_dnse_provider
```

## Ví dụ thực tế

### Ví dụ 1: Chart FPT với dữ liệu 3 tháng

```bash
export DNSE_SNAPSHOT_URL="https://api.dnse.com.vn/v1/snapshot?symbol={symbol}"
export DNSE_API_KEY="your_key"

python pnfchart.py FPT \
  --source dnse \
  --start 2024-11-01 \
  --end 2025-02-09 \
  --method hl \
  --reversal 3 \
  --scaling abs \
  --boxsize 1
```

### Ví dụ 2: Real-time snapshot cho VNM

```bash
python pnfchart.py VNM \
  --source dnse \
  --dnse-no-history \
  --timeframe 1m
```

### Ví dụ 3: Nhiều symbol với loop

```bash
for symbol in FPT VNM HPG MSN VCB; do
  echo "=== Chart for $symbol ==="
  python pnfchart.py $symbol --source dnse --dnse-no-history
  echo ""
done
```

## Xử lý lỗi

### Lỗi: "DNSE snapshot URL not configured"

**Nguyên nhân:** Chưa set biến môi trường.

**Giải pháp:**
```bash
export DNSE_SNAPSHOT_URL="https://your-api.com/snapshot?symbol={symbol}"
```

### Lỗi: "Empty DNSE response"

**Nguyên nhân:** API trả về null hoặc empty.

**Giải pháp:** Kiểm tra symbol, API key, hoặc endpoint.

### Lỗi: "DNSE snapshot missing price fields"

**Nguyên nhân:** Response không có field close/price.

**Giải pháp:** Kiểm tra format response hoặc tùy chỉnh provider.

### Lỗi: "Failed to load DNSE provider"

**Nguyên nhân:** Module provider không tìm thấy.

**Giải pháp:**
```bash
# Đảm bảo file dnse_provider.py có trong cùng thư mục
ls -la dnse_provider.py

# Hoặc dùng đường dẫn đầy đủ
python pnfchart.py FPT --source dnse --dnse-provider /path/to/my_provider
```

## Kiểm tra kết nối

Test nhanh với Python:

```python
from dnse_provider import fetch_snapshot

# Test snapshot
data = fetch_snapshot('FPT')
print(data)

# Output mẫu:
# {
#     'Date': ['2024-02-09'],
#     'Open': [64.0],
#     'High': [66.0],
#     'Low': [63.5],
#     'Close': [65.5]
# }
```

## So sánh với VNStock

| Feature | VNStock | DNSE |
|---------|---------|------|
| Lịch sử | ✅ Đầy đủ | ⚠️ Qua vnstock |
| Real-time | ❌ Không | ❌ Không (chỉ snapshot) |
| Volume | ✅ Có | ❌ Chưa có |
| API Key | ❌ Không cần | ⚠️ Tùy API |
| Tốc độ | ⏱️ Trung bình | ⚡ Nhanh (snapshot) |

## Kết hợp tối ưu

**Khuyến nghị:** Dùng DNSE + vnstock

```bash
# Lấy lịch sử từ vnstock, snapshot mới nhất từ DNSE
python pnfchart.py FPT \
  --source dnse \
  --start 2024-01-01 \
  --end 2025-02-09
```

Cách này cho phép:
- ✅ Có đầy đủ dữ liệu lịch sử
- ✅ Snapshot mới nhất từ DNSE nếu có
- ✅ Tự động merge không duplicate

## Tham khảo

- Provider code: [dnse_provider.py](dnse_provider.py)
- Data loader: [data_sources.py](data_sources.py) (function `load_dnse_data`)
- Main CLI: [pnfchart.py](pnfchart.py)
- VNStock guide: [README.md](README.md#L163-L189)

## Roadmap

- [ ] Hỗ trợ Volume (OHLCV)
- [ ] Batch multiple symbols
- [ ] Caching snapshot
- [ ] WebSocket streaming (nếu DNSE hỗ trợ)
- [ ] Historical OHLCV từ DNSE API (không qua vnstock)

---

**Lưu ý quan trọng:**
- Provider hiện tại chỉ lấy **OHLC** (không có Volume)
- DNSE snapshot không phải realtime streaming, chỉ là HTTP request lấy giá mới nhất
- Để có đầy đủ dữ liệu lịch sử, nên kết hợp với vnstock (mặc định)

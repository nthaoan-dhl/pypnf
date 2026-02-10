# Project Restructure - Clean Architecture

## ✅ Cấu trúc mới (Clean Architecture)

```
pypnf/
├── pypnf/                      # Main package
│   ├── core/                   # 🎯 Core: Point & Figure logic
│   │   ├── __init__.py
│   │   ├── chart.py            # PointFigureChart class
│   │   ├── testdata.py         # Test data utilities
│   │   └── html/               # HTML templates
│   │
│   ├── adapters/               # 🔌 Adapters: Data sources
│   │   ├── __init__.py
│   │   ├── base.py             # Base utilities
│   │   ├── yfinance.py         # Yahoo Finance
│   │   ├── ccxt.py             # Cryptocurrency (111+ exchanges)
│   │   ├── ctrader.py          # cTrader platform
│   │   ├── vnstock.py          # Vietnam stocks
│   │   └── dnse.py             # DNSE Lightspeed
│   │
│   ├── app/                    # 🚀 App: CLI application
│   │   ├── __init__.py
│   │   └── cli.py              # Command-line interface
│   │
│   └── __init__.py             # Package root
│
├── providers/                  # Provider implementations
│   ├── ctrader_provider.py
│   ├── dnse_provider.py
│   └── mock_dnse_provider.py
│
├── examples/                   # Example scripts
│   ├── example_ccxt_usage.py
│   └── demo_dnse_mock.py
│
├── utils/                      # Utility scripts
│   ├── check_ctrader_symbols.py
│   ├── check_symbol_digits.py
│   ├── get_ctrader_account_id.py
│   ├── test_ctrader_http.py
│   ├── test_dnse_snapshot.py
│   └── test_gap_filling.py
│
├── tests/                      # Unit tests
│   ├── test_*.py
│   └── ...
│
├── docs/                       # Documentation
│   ├── CCXT_QUICK_START.md
│   ├── DNSE_QUICK_START.md
│   ├── CTRADER_QUICK_START.md
│   └── ...
│
├── pnfchart.py                 # CLI wrapper (backward compatible)
├── data_sources.py             # [DEPRECATED] Use pypnf.adapters
├── README.md
└── setup.py
```

## 🎯 Triết lý thiết kế

### 1. **Core** - Business Logic
- Chứa thuật toán Point & Figure chart
- Không phụ thuộc vào data source
- Pure calculations, testable

### 2. **Adapters** - Data Integration
- Mỗi data source một adapter riêng
- Interface thống nhất: `load_data()`
- Easy to add new sources
- Adapters handle data normalization

### 3. **App** - User Interface
- CLI application
- Orchestrates core + adapters
- User-facing logic

## 📦 Imports mới

### Cách 1: Import từ core
```python
from pypnf.core import PointFigureChart, dataset
```

### Cách 2: Import từ main package (recommended)
```python
from pypnf import PointFigureChart, dataset
```

### Cách 3: Import adapters
```python
from pypnf.adapters import (
    load_yfinance_data,
    load_ccxt_data,
    load_ctrader_data,
    load_vnstock_data,
    load_dnse_data,
)
```

### Cách 4: Import specific adapter
```python
from pypnf.adapters.ccxt import load_data, get_available_exchanges
```

## 🚀 Usage

### CLI (backward compatible)
```bash
# Old way still works
python pnfchart.py BTC/USDT --source ccxt --exchange binance

# New way (using module)
python -m pypnf.app.cli BTC/USDT --source ccxt --exchange binance
```

### Python API
```python
from pypnf import PointFigureChart
from pypnf.adapters import load_ccxt_data

# Load data
data = load_ccxt_data('binance', 'BTC/USDT', '2024-01-01', '2024-12-31', '1d')

# Create chart
pnf = PointFigureChart(
    ts=data,
    method='h/l',
    reversal=3,
    boxsize=100,
    scaling='abs',
    title='BTC/USDT'
)

print(pnf)
```

## ✅ Benefits

### 1. **Separation of Concerns**
- Core logic không biết về data sources
- Adapters không biết về charting logic
- App chỉ orchestrate

### 2. **Maintainability**
- Mỗi component có responsibility rõ ràng
- Easy to find code
- Easy to test

### 3. **Extensibility**
- Add new adapter: tạo file mới trong `adapters/`
- Add new chart method: sửa `core/chart.py`
- Add new CLI feature: sửa `app/cli.py`

### 4. **Clean imports**
- No more `from data_sources import load_ccxt_data`
- Clean: `from pypnf.adapters.ccxt import load_data`
- Or: `from pypnf.adapters import load_ccxt_data`

### 5. **Professional structure**
- Follows Python package best practices
- Similar to Django, Flask structure
- Easy for new contributors to understand

## 📝 Migration Guide

### Old code:
```python
from pypnf import PointFigureChart
from data_sources import load_ccxt_data

data = load_ccxt_data('binance', 'BTC/USDT', '2024-01-01', '2024-12-31')
pnf = PointFigureChart(data, method='h/l', reversal=3)
```

### New code (Option 1 - Minimal changes):
```python
from pypnf import PointFigureChart
from pypnf.adapters import load_ccxt_data  # Just change import!

data = load_ccxt_data('binance', 'BTC/USDT', '2024-01-01', '2024-12-31')
pnf = PointFigureChart(data, method='h/l', reversal=3)
```

### New code (Option 2 - More explicit):
```python
from pypnf.core import PointFigureChart
from pypnf.adapters.ccxt import load_data

data = load_data('binance', 'BTC/USDT', '2024-01-01', '2024-12-31')
pnf = PointFigureChart(data, method='h/l', reversal=3)
```

## 🧪 Testing

All tests pass with new structure:
```bash
✅ Core imports working
✅ Adapter imports working
✅ Main package import working
✅ CLI working (pnfchart.py)
✅ End-to-end test successful (BTC/USDT chart generated)
```

## 🔄 Backward Compatibility

- ✅ `pnfchart.py` still works (wrapper to new cli)
- ✅ `from pypnf import PointFigureChart` still works
- ⚠️ `from data_sources import *` deprecated but still exists
- ✅ All old scripts continue to work

## 📚 Next Steps

1. ✅ Structure created
2. ✅ All files moved
3. ✅ Imports updated
4. ✅ Tests passed
5. ⏭️ Update documentation files
6. ⏭️ Delete old files (data_sources.py, pypnf/chart.py, etc.)
7. ⏭️ Update setup.py
8. ⏭️ Update README.md

## 🎯 Summary

**Before:**
- All adapters in one giant `data_sources.py` (482 lines)
- Core logic in `pypnf/chart.py`
- Utilities scattered in root

**After:**
- Clean separation: `core/`, `adapters/`, `app/`
- Each adapter in its own file (~150 lines each)
- Utilities organized in folders
- Professional structure
- Easy to maintain and extend

**Result:** Production-ready package structure! 🚀

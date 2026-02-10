# cTrader Quick Start Guide

## ✅ Working Perfectly

### Forex Pairs (Recommended)
```bash
# EURUSD - Hourly chart
python pnfchart.py EURUSD --source ctrader --timeframe h1 --start 2026-01-01 --end 2026-02-07

# GBPUSD - Daily chart
python pnfchart.py GBPUSD --source ctrader --timeframe d1 --columns 50

# AUDUSD - 15-minute chart
python pnfchart.py AUDUSD --source ctrader --timeframe m15 --start 2026-02-01 --end 2026-02-07

# Multiple pairs available:
# EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, AUDJPY, USDCAD, NZDUSD, CADJPY, CHFJPY
```

## ⚠️ Known Issues (Use Test Mode Instead)

### Metals & Crypto (Pricing Issue)
Due to account-specific digits encoding, these symbols show incorrect prices:
- XAUUSD (Gold) - shows ~4,960,740 instead of ~2,000
- BTCUSD (Bitcoin) - pricing incorrect
- XAGUSD (Silver) - pricing incorrect

**Workaround:** Use built-in test data mode (no credentials needed):
```bash
# These generate realistic synthetic data
python pnfchart.py XAUUSD --source ctrader --timeframe d1
python pnfchart.py BTCUSD --source ctrader --timeframe h1
```

## 💡 Best Practices

### Always Specify Date Range
```bash
--start 2026-01-01 --end 2026-02-07
```

Default is 2024-01-01 to today, which may be too much data.

### Adjust Box Size for Different Scales
```bash
# Small movements (intraday)
--boxsize 0.01

# Medium movements
--boxsize 0.05

# Large movements
--boxsize 0.1 --boxsize 0.5
```

### Timeframe Options
```bash
--timeframe m1    # 1 minute
--timeframe m5    # 5 minutes  
--timeframe m15   # 15 minutes
--timeframe m30   # 30 minutes
--timeframe h1    # 1 hour (recommended)
--timeframe h4    # 4 hours
--timeframe d1    # 1 day
--timeframe w1    # 1 week
```

## 🔧 Examples

### Recent Price Action
```bash
python pnfchart.py EURUSD --source ctrader --timeframe h1 \
  --start 2026-02-01 --end 2026-02-07 --columns 40
```

### Intraday Analysis
```bash
python pnfchart.py GBPUSD --source ctrader --timeframe m15 \
  --start 2026-02-06 --end 2026-02-07 --boxsize 0.01 --columns 50
```

### Long-term Trends
```bash
python pnfchart.py USDJPY --source ctrader --timeframe d1 \
  --start 2025-12-01 --end 2026-02-07 --columns 0
```

### Custom Parameters
```bash
python pnfchart.py EURUSD --source ctrader \
  --start 2026-01-15 --end 2026-02-07 \
  --timeframe h1 \
  --method h/l \
  --boxsize 0.02 \
  --reversal 3 \
  --columns 40
```

## 🚀 What Works

✅ Live data from cTrader OpenAPI  
✅ Data extends to current date (Feb 7, 2026)  
✅ All major forex pairs  
✅ Multiple timeframes (m1 to w1)  
✅ All Point & Figure methods  
✅ Trendlines, breakouts, patterns  
✅ Test mode fallback (no credentials needed)

## 📝 Notes

- **Default date range:** 2024-01-01 to today
- **Data freshness:** Updated to February 7, 2026
- **Symbol IDs:** Correct for account 24570842
- **Library:** Official ctrader-open-api v0.9.2

## 🆘 Troubleshooting

### No data or errors?
Check credentials in `.env`:
```bash
CTRADER_CLIENT_ID=...
CTRADER_CLIENT_SECRET=...
CTRADER_ACCESS_TOKEN=...
CTRADER_ACCOUNT_ID=...
```

### Chart too small?
```bash
--columns 0          # Show all columns
--boxsize 0.01       # Smaller boxes (more detail)
--start 2025-01-01   # More historical data
```

### Chart too large?
```bash
--columns 40         # Limit to 40 columns
--boxsize 0.1        # Larger boxes (less detail)
--start 2026-01-15   # Less historical data
```

### Test data instead of live?
System automatically falls back to test data if:
- Missing credentials
- API connection fails
- Symbol not found

---

**Last Updated:** February 7, 2026  
**Status:** Production Ready (Forex pairs)

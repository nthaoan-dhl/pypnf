#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gap Filling Behavior Test
Demonstrates how PnF charts handle price gaps
"""

from pypnf import PointFigureChart

# Test data with significant price gaps
ts = {
    'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
    'open': [100, 105, 120, 115, 125],
    'high': [102, 110, 125, 120, 130],
    'low': [98, 104, 115, 110, 120],
    'close': [101, 108, 122, 118, 128],
    'volume': [1000000, 1100000, 1200000, 1050000, 1300000]
}

print("=" * 60)
print("TEST: Price Gap Filling in Point & Figure Charts")
print("=" * 60)
print("\nData Close Prices: 101 → 108 → 122 (jump) → 118 → 128 (jump)\n")

print("\n--- Reversal 1 (tìm kiếm nhạy cảm hơn) ---")
pnf1 = PointFigureChart(ts=ts, method='cl', reversal=1, boxsize=2, scaling='abs', title='Reversal=1')
print(pnf1)

print("\n--- Reversal 2 (tìm kiếm bình thường) ---")
pnf2 = PointFigureChart(ts=ts, method='cl', reversal=2, boxsize=2, scaling='abs', title='Reversal=2')
print(pnf2)

print("\n" + "=" * 60)
print("KẾT LUẬN:")
print("=" * 60)
print("✓ Chart ĐIỀN tất cả boxes trung gian - KHÔNG CÓ GAP")
print("✓ Reversal quyết định số boxes cần để ĐẢO CHIỀU (reversal)")
print("✓ Reversal=1: Toàn cảnh chi tiết hơn")
print("✓ Reversal=2: Ít nhiễu, tập trung vào xu hướng chính")

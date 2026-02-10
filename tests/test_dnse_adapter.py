#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mock tests for DNSE adapter OHLCV data fetching
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pytest
import importlib

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# Mock DNSE snapshot data
MOCK_DNSE_SNAPSHOT = {
    'Date': ['2026-02-10 09:00:00', '2026-02-10 09:01:00', '2026-02-10 09:02:00'],
    'Open': [25.5, 25.6, 25.7],
    'High': [25.8, 25.9, 26.0],
    'Low': [25.4, 25.5, 25.6],
    'Close': [25.7, 25.8, 25.9],
}

# Mock vnstock historical data
MOCK_VNSTOCK_HISTORY = {
    'Date': ['2026-02-08', '2026-02-09'],
    'Open': [24.5, 25.0],
    'High': [24.8, 25.3],
    'Low': [24.2, 24.9],
    'Close': [24.6, 25.2],
}

# Combined data (history + snapshot)
MOCK_COMBINED_DATA = {
    'Date': ['2026-02-08', '2026-02-09', '2026-02-10 09:00:00', '2026-02-10 09:01:00', '2026-02-10 09:02:00'],
    'Open': [24.5, 25.0, 25.5, 25.6, 25.7],
    'High': [24.8, 25.3, 25.8, 25.9, 26.0],
    'Low': [24.2, 24.9, 25.4, 25.5, 25.6],
    'Close': [24.6, 25.2, 25.7, 25.8, 25.9],
}


class TestDNSEAdapter:
    """Test DNSE adapter with mocked data"""

    @patch('pnfchart.adapters.vnstock.load_data')
    def test_load_dnse_snapshot_only(self, mock_vnstock):
        """Test loading DNSE snapshot without history"""
        from pnfchart.adapters.dnse import load_dnse_data
        
        # Create mock provider
        mock_provider = MagicMock()
        mock_provider.fetch_snapshot = Mock(return_value=MOCK_DNSE_SNAPSHOT)
        
        with patch('importlib.import_module', return_value=mock_provider):
            result = load_dnse_data(
                symbol='VCB',
                start_date='2026-02-10',
                end_date='2026-02-10',
                timeframe='1m',
                include_history=False
            )
        
        assert result == MOCK_DNSE_SNAPSHOT
        assert len(result['Date']) == 3
        assert result['Close'][-1] == 25.9
        mock_provider.fetch_snapshot.assert_called_once()
        mock_vnstock.assert_not_called()

    @patch('pnfchart.adapters.vnstock.load_data')
    def test_load_dnse_with_history(self, mock_vnstock):
        """Test loading DNSE with historical data from vnstock"""
        from pnfchart.adapters.dnse import load_dnse_data
        
        # Setup mock vnstock to return history
        mock_vnstock.return_value = MOCK_VNSTOCK_HISTORY.copy()
        
        # Create mock provider
        mock_provider = MagicMock()
        mock_provider.fetch_snapshot = Mock(return_value=MOCK_DNSE_SNAPSHOT)
        
        with patch('importlib.import_module', return_value=mock_provider):
            result = load_dnse_data(
                symbol='VCB',
                start_date='2026-02-08',
                end_date='2026-02-10',
                timeframe='1m',
                include_history=True
            )
        
        # Should combine history and snapshot
        assert len(result['Date']) == 5
        assert result['Date'][0] == '2026-02-08'
        assert result['Date'][-1] == '2026-02-10 09:02:00'
        assert result['Close'][0] == 24.6  # From history
        assert result['Close'][-1] == 25.9  # From snapshot
        mock_vnstock.assert_called_once()

    @patch('pnfchart.adapters.vnstock.load_data')
    def test_load_dnse_empty_snapshot(self, mock_vnstock):
        """Test when DNSE returns empty snapshot"""
        from pnfchart.adapters.dnse import load_dnse_data
        
        # Setup mock vnstock
        mock_vnstock.return_value = MOCK_VNSTOCK_HISTORY.copy()
        
        # Create mock provider returning empty data
        mock_provider = MagicMock()
        mock_provider.fetch_snapshot = Mock(return_value=None)
        
        with patch('importlib.import_module', return_value=mock_provider):
            result = load_dnse_data(
                symbol='VCB',
                start_date='2026-02-08',
                end_date='2026-02-10',
                timeframe='1m',
                include_history=True
            )
        
        # Should only return history when snapshot is empty
        assert result == MOCK_VNSTOCK_HISTORY
        assert len(result['Date']) == 2

    def test_load_dnse_no_provider(self):
        """Test error handling when provider module not found"""
        from pnfchart.adapters.dnse import load_dnse_data
        
        with patch('importlib.import_module', side_effect=ModuleNotFoundError("No module named 'dnse_provider'")):
            with pytest.raises(ValueError, match="Failed to load DNSE provider"):
                load_dnse_data(
                    symbol='VCB',
                    start_date='2026-02-10',
                    end_date='2026-02-10',
                    timeframe='1m',
                    include_history=False
                )

    def test_load_dnse_missing_fetch_snapshot(self):
        """Test error when provider doesn't have fetch_snapshot method"""
        from pnfchart.adapters.dnse import load_dnse_data
        
        # Create mock provider without fetch_snapshot
        mock_provider = MagicMock(spec=[])
        
        with patch('importlib.import_module', return_value=mock_provider):
            with pytest.raises(ValueError, match="must define fetch_snapshot"):
                load_dnse_data(
                    symbol='VCB',
                    start_date='2026-02-10',
                    end_date='2026-02-10',
                    timeframe='1m',
                    include_history=False
                )

    @patch('pnfchart.adapters.vnstock.load_data')
    def test_load_dnse_snapshot_not_newer(self, mock_vnstock):
        """Test when snapshot date is not newer than history"""
        from pnfchart.adapters.dnse import load_dnse_data
        
        # Setup mock vnstock
        mock_vnstock.return_value = MOCK_VNSTOCK_HISTORY.copy()
        
        # Snapshot with older date
        old_snapshot = {
            'Date': ['2026-02-07 09:00:00'],
            'Open': [24.0],
            'High': [24.2],
            'Low': [23.9],
            'Close': [24.1],
        }
        
        mock_provider = MagicMock()
        mock_provider.fetch_snapshot = Mock(return_value=old_snapshot)
        
        with patch('importlib.import_module', return_value=mock_provider):
            result = load_dnse_data(
                symbol='VCB',
                start_date='2026-02-08',
                end_date='2026-02-10',
                timeframe='1m',
                include_history=True
            )
        
        # Should only return history since snapshot is older
        assert len(result['Date']) == 2
        assert result['Date'][-1] == '2026-02-09'

    def test_load_dnse_custom_provider(self):
        """Test using custom provider module name"""
        from pnfchart.adapters.dnse import load_dnse_data
        
        mock_provider = MagicMock()
        mock_provider.fetch_snapshot = Mock(return_value=MOCK_DNSE_SNAPSHOT)
        
        with patch('importlib.import_module', return_value=mock_provider) as mock_import:
            result = load_dnse_data(
                symbol='VCB',
                start_date='2026-02-10',
                end_date='2026-02-10',
                timeframe='1m',
                provider_module='my_custom_provider',
                include_history=False
            )
        
        # Verify custom module was requested
        mock_import.assert_called_with('my_custom_provider')
        assert result == MOCK_DNSE_SNAPSHOT


def test_dnse_data_structure():
    """Test that returned data has correct structure"""
    from pnfchart.adapters.dnse import load_dnse_data
    
    mock_provider = MagicMock()
    mock_provider.fetch_snapshot = Mock(return_value=MOCK_DNSE_SNAPSHOT)
    
    with patch('importlib.import_module', return_value=mock_provider):
        result = load_dnse_data(
            symbol='VCB',
            start_date='2026-02-10',
            end_date='2026-02-10',
            timeframe='1m',
            include_history=False
        )
    
    # Verify structure
    assert isinstance(result, dict)
    assert 'Date' in result
    assert 'Open' in result
    assert 'High' in result
    assert 'Low' in result
    assert 'Close' in result
    
    # Verify all arrays have same length
    length = len(result['Date'])
    assert len(result['Open']) == length
    assert len(result['High']) == length
    assert len(result['Low']) == length
    assert len(result['Close']) == length


def test_dnse_ohlc_validity():
    """Test that OHLC values are valid (High >= Low, etc.)"""
    from pnfchart.adapters.dnse import load_dnse_data
    
    mock_provider = MagicMock()
    mock_provider.fetch_snapshot = Mock(return_value=MOCK_DNSE_SNAPSHOT)
    
    with patch('importlib.import_module', return_value=mock_provider):
        result = load_dnse_data(
            symbol='VCB',
            start_date='2026-02-10',
            end_date='2026-02-10',
            timeframe='1m',
            include_history=False
        )
    
    # Verify OHLC relationships
    for i in range(len(result['Date'])):
        high = result['High'][i]
        low = result['Low'][i]
        open_price = result['Open'][i]
        close = result['Close'][i]
        
        assert high >= low, f"High {high} should be >= Low {low}"
        assert high >= open_price, f"High {high} should be >= Open {open_price}"
        assert high >= close, f"High {high} should be >= Close {close}"
        assert low <= open_price, f"Low {low} should be <= Open {open_price}"
        assert low <= close, f"Low {low} should be <= Close {close}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

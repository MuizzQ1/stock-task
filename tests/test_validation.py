# tests/test_validation.py
from aapl_stock.validation import validate_stock_data


def make_row(**overrides):
    """Single row of valid stock data with overrides for testing"""

    row = {
        "stock_code": "AAPL",
        "interval_time": "1d",
        "ts": "2026-01-02T00:00:00-05:00",
        "stock_open": 185.0,
        "stock_high": 190.0,
        "stock_low": 184.0,
        "stock_close": 188.0,
        "volume": 50_000_000,
    }
    row.update(overrides)
    return [row]


def test_valid_row_passes():
    valid, rejected = validate_stock_data(make_row())
    assert len(valid) == 1
    assert rejected == []


def test_null_price_rejected():
    valid, rejected = validate_stock_data(make_row(stock_close=None))
    assert valid == []
    assert len(rejected) == 1


def test_string_in_volume_rejected():
    valid, rejected = validate_stock_data(make_row(volume="not_a_number"))
    assert valid == []
    assert len(rejected) == 1


def test_negative_price_rejected():
    valid, rejected = validate_stock_data(make_row(stock_open=-5.0))
    assert valid == []
    assert len(rejected) == 1


def test_invalid_interval_rejected():
    valid, rejected = validate_stock_data(make_row(interval_time="5min"))
    assert valid == []
    assert len(rejected) == 1


def test_partial_batch_keeps_good_rows():
    """Test batch with valid and invalid rows. Only valid rows should be returned."""
    rows = (
        make_row()
        + make_row(stock_open=-1.0)
        + make_row(ts="2026-01-03T00:00:00-05:00")
    )
    valid, rejected = validate_stock_data(rows)
    assert len(valid) == 2
    assert len(rejected) == 1

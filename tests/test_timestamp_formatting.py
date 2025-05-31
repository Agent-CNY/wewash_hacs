"""Tests for timestamp formatting functions."""
from datetime import datetime
import time
import pytest
from freezegun import freeze_time

from custom_components.wewash.sensor import format_timestamp, get_remaining_minutes


@pytest.mark.parametrize(
    "timestamp,expected_format",
    [
        (1748695512245, "2025-05-31 02:25:12"),  # Example timestamp
        (None, None),  # Test with None
    ],
)
def test_format_timestamp(timestamp, expected_format):
    """Test the format_timestamp function."""
    if timestamp is not None:
        # Use a fixed datetime for testing
        expected = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
        assert format_timestamp(timestamp) == expected
    else:
        assert format_timestamp(timestamp) is None


@freeze_time("2025-05-31 00:00:00")
def test_get_remaining_minutes():
    """Test the get_remaining_minutes function."""
    # Freeze time at 2025-05-31 00:00:00
    # Set current time in milliseconds
    current_time_ms = int(datetime(2025, 5, 31, 0, 0, 0).timestamp() * 1000)
    
    # Test cases
    # 1. Timeout is 30 minutes later
    timeout_30min_later = current_time_ms + (30 * 60 * 1000)
    assert get_remaining_minutes(timeout_30min_later) == 30
    
    # 2. Timeout is 1 hour later
    timeout_1h_later = current_time_ms + (60 * 60 * 1000)
    assert get_remaining_minutes(timeout_1h_later) == 60
    
    # 3. Timeout is in the past (should return 0, not negative)
    timeout_past = current_time_ms - (10 * 60 * 1000)
    assert get_remaining_minutes(timeout_past) == 0
    
    # 4. None timeout
    assert get_remaining_minutes(None) is None

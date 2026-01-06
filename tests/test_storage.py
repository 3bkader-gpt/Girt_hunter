"""Unit tests for storage models."""
import pytest
from datetime import datetime


def test_gift_model():
    """Test Gift model creation."""
    from src.storage.models import Gift
    
    gift = Gift(
        id=12345,
        name="Test Gift",
        price=1000,
        total_amount=50000,
        available_amount=45000,
        is_limited=True,
        is_sold_out=False,
        upgrade_price=5000,
    )
    
    assert gift.id == 12345
    assert gift.name == "Test Gift"
    assert gift.price == 1000
    assert gift.is_upgradable is True
    assert gift.availability_percentage == 90.0


def test_gift_not_upgradable():
    """Test gift without upgrade price."""
    from src.storage.models import Gift
    
    gift = Gift(
        id=99999,
        name="Basic Gift",
        price=500,
        total_amount=100000,
        available_amount=50000,
        is_limited=False,
        upgrade_price=None,
    )
    
    assert gift.is_upgradable is False


def test_gift_zero_availability():
    """Test gift with zero total amount."""
    from src.storage.models import Gift
    
    gift = Gift(
        id=11111,
        name="Empty Gift",
        price=100,
        total_amount=0,
        available_amount=0,
    )
    
    assert gift.availability_percentage == 0.0


def test_purchase_model():
    """Test Purchase model creation."""
    from src.storage.models import Purchase
    
    purchase = Purchase(
        gift_id=12345,
        gift_name="Test Gift",
        recipient_id=987654,
        recipient_username="@testuser",
        price=1000,
        quantity=3,
        total_cost=3000,
        is_partial=False,
    )
    
    assert purchase.gift_id == 12345
    assert purchase.quantity == 3
    assert purchase.total_cost == 3000


def test_daily_stats_model():
    """Test DailyStats model creation."""
    from src.storage.models import DailyStats
    
    stats = DailyStats(
        date="2026-01-06",
        total_spent=5000,
        gifts_purchased=10,
        gifts_checked=500,
        errors_count=2,
    )
    
    assert stats.date == "2026-01-06"
    assert stats.total_spent == 5000


print("✅ All storage tests passed!")

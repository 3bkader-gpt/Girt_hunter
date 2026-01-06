"""Unit tests for configuration settings."""
import os
import pytest
from pathlib import Path

# Set test environment variables before importing settings
os.environ["TELEGRAM_API_ID"] = "12345"
os.environ["TELEGRAM_API_HASH"] = "test_hash_abc123"
os.environ["TELEGRAM_PHONE_NUMBER"] = "+1234567890"


def test_gift_range_validation():
    """Test GiftRange model validation."""
    from src.config.settings import GiftRange
    
    # Valid range
    range_config = GiftRange(
        name="Test Range",
        min_price=100,
        max_price=500,
        supply_limit=10000,
        quantity_per_recipient=2,
        recipients=["@testuser", 123456],
    )
    
    assert range_config.name == "Test Range"
    assert range_config.min_price == 100
    assert range_config.max_price == 500
    assert len(range_config.recipients) == 2


def test_gift_range_max_price_validation():
    """Test that max_price must be >= min_price."""
    from src.config.settings import GiftRange
    
    with pytest.raises(ValueError, match="max_price"):
        GiftRange(
            name="Invalid Range",
            min_price=500,
            max_price=100,  # Invalid: less than min_price
        )


def test_phone_validation():
    """Test phone number validation."""
    from src.config.settings import TelegramSettings
    
    # Valid phone (from environment)
    settings = TelegramSettings()
    assert settings.phone_number.startswith("+")


def test_notification_types_defaults():
    """Test notification type defaults."""
    from src.config.settings import NotificationTypes
    
    types = NotificationTypes()
    
    assert types.purchase_success is True
    assert types.balance_low is True
    assert types.errors is True


def test_budget_settings_defaults():
    """Test budget settings defaults."""
    from src.config.settings import BudgetSettings
    
    budget = BudgetSettings()
    
    assert budget.daily_limit == 0  # Unlimited
    assert budget.reserve_balance == 0


def test_app_config_defaults():
    """Test AppConfig with default values."""
    from src.config.settings import AppConfig
    
    config = AppConfig()
    
    assert config.telegram.interval_seconds == 10
    assert config.telegram.max_retries == 3
    assert config.notifications.channel_id == -100
    assert config.language == "EN"


print("✅ All config tests passed!")

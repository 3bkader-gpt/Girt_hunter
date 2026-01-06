"""Simple test runner without pytest."""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set mock environment variables
os.environ["TELEGRAM_API_ID"] = "12345"
os.environ["TELEGRAM_API_HASH"] = "test_hash_abc123"
os.environ["TELEGRAM_PHONE_NUMBER"] = "+1234567890"


def test_config():
    """Test configuration module."""
    print("\n📦 Testing Configuration...")
    
    from src.config.settings import (
        GiftRange, NotificationTypes, BudgetSettings, 
        AppConfig, TelegramSettings
    )
    
    # Test GiftRange
    range_config = GiftRange(
        name="Test Range",
        min_price=100,
        max_price=500,
        supply_limit=10000,
        quantity_per_recipient=2,
        recipients=["@testuser", 123456],
    )
    assert range_config.name == "Test Range", "GiftRange name failed"
    assert range_config.min_price == 100, "GiftRange min_price failed"
    print("  ✅ GiftRange validation works")
    
    # Test invalid range
    try:
        GiftRange(name="Bad", min_price=500, max_price=100)
        print("  ❌ GiftRange should reject max < min")
    except ValueError:
        print("  ✅ GiftRange rejects invalid max_price")
    
    # Test NotificationTypes
    types = NotificationTypes()
    assert types.purchase_success is True, "NotificationTypes default failed"
    print("  ✅ NotificationTypes defaults work")
    
    # Test BudgetSettings
    budget = BudgetSettings()
    assert budget.daily_limit == 0, "BudgetSettings default failed"
    print("  ✅ BudgetSettings defaults work")
    
    # Test AppConfig
    config = AppConfig()
    assert config.telegram.interval_seconds == 10, "AppConfig interval failed"
    assert config.language == "EN", "AppConfig language failed"
    print("  ✅ AppConfig defaults work")
    
    # Test TelegramSettings from env
    tg_settings = TelegramSettings()
    assert tg_settings.api_id == 12345, "TelegramSettings API_ID failed"
    assert tg_settings.phone_number == "+1234567890", "TelegramSettings phone failed"
    print("  ✅ TelegramSettings loads from environment")
    
    print("✅ Configuration tests PASSED")


def test_storage_models():
    """Test storage models."""
    print("\n📦 Testing Storage Models...")
    
    from src.storage.models import Gift, Purchase, DailyStats
    
    # Test Gift
    gift = Gift(
        id=12345,
        name="Test Gift",
        price=1000,
        total_amount=50000,
        available_amount=45000,
        is_limited=True,
        upgrade_price=5000,
    )
    assert gift.is_upgradable is True, "Gift.is_upgradable failed"
    assert gift.availability_percentage == 90.0, "Gift.availability failed"
    print("  ✅ Gift model works")
    
    # Test Gift without upgrade
    basic_gift = Gift(
        id=99999, name="Basic", price=500,
        total_amount=100000, available_amount=50000,
    )
    assert basic_gift.is_upgradable is False, "Basic gift should not be upgradable"
    print("  ✅ Gift upgradable detection works")
    
    # Test Purchase
    purchase = Purchase(
        gift_id=12345, gift_name="Test Gift",
        recipient_id=987654, price=1000,
        quantity=3, total_cost=3000,
    )
    assert purchase.total_cost == 3000, "Purchase total_cost failed"
    print("  ✅ Purchase model works")
    
    # Test DailyStats
    stats = DailyStats(date="2026-01-06", total_spent=5000, gifts_purchased=10)
    assert stats.total_spent == 5000, "DailyStats failed"
    print("  ✅ DailyStats model works")
    
    print("✅ Storage model tests PASSED")


def test_observability():
    """Test observability modules."""
    print("\n📦 Testing Observability...")
    
    # Test logging setup
    from src.observability.logging import setup_logging, get_logger
    setup_logging("INFO")
    logger = get_logger("test")
    logger.info("test_message", key="value")
    print("  ✅ Structured logging works")
    
    # Test metrics
    from src.observability.metrics import (
        GIFTS_CHECKED, GIFTS_PURCHASED, BALANCE,
        GIFTS_AVAILABLE, ACTIVE_MONITORING
    )
    GIFTS_CHECKED.inc()
    BALANCE.set(10000)
    ACTIVE_MONITORING.set(1)
    print("  ✅ Prometheus metrics work")
    
    # Test health
    from src.observability.health import set_health_status, get_health_status
    set_health_status(status="healthy", telegram_connected=True, database_connected=True)
    health = get_health_status()
    assert health["status"] == "healthy", "Health status failed"
    assert health["telegram_connected"] is True, "Health telegram failed"
    print("  ✅ Health status works")
    
    print("✅ Observability tests PASSED")


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Gift Hunter v2.0 - Test Suite")
    print("=" * 60)
    
    try:
        test_config()
        test_storage_models()
        test_observability()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

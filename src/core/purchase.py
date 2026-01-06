"""Purchase engine with balance management."""
import asyncio
from datetime import datetime
from typing import Any, NamedTuple

from src.config import get_settings, GiftRange
from src.observability import get_logger
from src.observability.metrics import (
    GIFTS_PURCHASED,
    PURCHASES_FAILED,
    BALANCE,
    PURCHASE_DURATION,
)
from src.storage import get_session
from src.storage.database import record_purchase

from .client import TelegramClientWrapper

logger = get_logger(__name__)


class PurchaseResult(NamedTuple):
    """Result of a purchase attempt."""
    success: bool
    purchased_quantity: int
    requested_quantity: int
    is_partial: bool
    remaining_balance: int
    error: str | None = None


class PurchaseEngine:
    """Handles gift purchases with balance management."""
    
    def __init__(self, client: TelegramClientWrapper) -> None:
        """Initialize the purchase engine.
        
        Args:
            client: Telegram client wrapper
        """
        self.client = client
        
        settings = get_settings()
        self.gift_config = settings.app.gifts
        self.budget_config = settings.app.budget
        self.notification_channel = settings.app.notifications.channel_id
        
        self._daily_spent = 0
        self._last_reset_date: str | None = None
    
    async def process_gift(self, gift: Any) -> list[PurchaseResult]:
        """Process a gift and purchase for all matching recipients.
        
        Args:
            gift: Gift object from Telegram
            
        Returns:
            List of purchase results
        """
        results = []
        
        # Extract gift properties
        gift_id = getattr(gift, "id", gift.get("id") if isinstance(gift, dict) else None)
        gift_name = getattr(gift, "title", gift.get("title") if isinstance(gift, dict) else "Unknown")
        price = getattr(gift, "stars", gift.get("stars") if isinstance(gift, dict) else 0)
        
        if not gift_id or price <= 0:
            return results
        
        # Find matching ranges
        matching_ranges = self._find_matching_ranges(price, gift)
        
        if not matching_ranges:
            return results
        
        # Get current balance
        balance = await self.client.get_balance()
        BALANCE.set(balance)
        
        # Check budget limits
        self._check_daily_reset()
        
        for range_config in matching_ranges:
            for recipient in range_config.recipients:
                result = await self._purchase_for_recipient(
                    gift_id=gift_id,
                    gift_name=gift_name,
                    price=price,
                    recipient=recipient,
                    quantity=range_config.quantity_per_recipient,
                    balance=balance,
                )
                results.append(result)
                
                # Update balance
                if result.success:
                    balance = result.remaining_balance
                    BALANCE.set(balance)
        
        return results
    
    def _find_matching_ranges(self, price: int, gift: Any) -> list[GiftRange]:
        """Find all gift ranges that match this gift.
        
        Args:
            price: Gift price
            gift: Gift object
            
        Returns:
            List of matching GiftRange configs
        """
        total_amount = getattr(gift, "total_amount", gift.get("total_amount") if isinstance(gift, dict) else 0)
        upgrade_price = getattr(gift, "upgrade_stars", gift.get("upgrade_stars") if isinstance(gift, dict) else None)
        
        matching = []
        
        for range_config in self.gift_config.ranges:
            if range_config.min_price <= price <= range_config.max_price:
                if total_amount <= range_config.supply_limit:
                    if range_config.upgradable_only and upgrade_price is None:
                        continue
                    if range_config.recipients:
                        matching.append(range_config)
        
        return matching
    
    async def _purchase_for_recipient(
        self,
        gift_id: int,
        gift_name: str,
        price: int,
        recipient: str | int,
        quantity: int,
        balance: int,
    ) -> PurchaseResult:
        """Purchase gifts for a specific recipient.
        
        Args:
            gift_id: Gift ID
            gift_name: Gift name for logging
            price: Price per gift
            recipient: Username or user ID
            quantity: Desired quantity
            balance: Current balance
            
        Returns:
            PurchaseResult
        """
        start_time = datetime.utcnow()
        
        # Resolve recipient ID
        recipient_id = await self._resolve_recipient(recipient)
        if not recipient_id:
            PURCHASES_FAILED.labels(reason="invalid_recipient").inc()
            return PurchaseResult(
                success=False,
                purchased_quantity=0,
                requested_quantity=quantity,
                is_partial=False,
                remaining_balance=balance,
                error=f"Could not resolve recipient: {recipient}",
            )
        
        # Check if recipient is blacklisted
        if recipient_id in self.gift_config.blacklist_recipients:
            return PurchaseResult(
                success=False,
                purchased_quantity=0,
                requested_quantity=quantity,
                is_partial=False,
                remaining_balance=balance,
                error="Recipient is blacklisted",
            )
        
        # Calculate affordable quantity
        effective_balance = balance - self.budget_config.reserve_balance
        if effective_balance <= 0:
            PURCHASES_FAILED.labels(reason="reserve_balance").inc()
            return PurchaseResult(
                success=False,
                purchased_quantity=0,
                requested_quantity=quantity,
                is_partial=False,
                remaining_balance=balance,
                error="Balance below reserve threshold",
            )
        
        # Check daily limit
        if self.budget_config.daily_limit > 0:
            remaining_daily = self.budget_config.daily_limit - self._daily_spent
            max_from_daily = remaining_daily // price
            quantity = min(quantity, max_from_daily)
        
        # Calculate max affordable
        max_affordable = min(quantity, effective_balance // price)
        
        if max_affordable <= 0:
            PURCHASES_FAILED.labels(reason="insufficient_balance").inc()
            return PurchaseResult(
                success=False,
                purchased_quantity=0,
                requested_quantity=quantity,
                is_partial=False,
                remaining_balance=balance,
                error="Insufficient balance",
            )
        
        is_partial = max_affordable < quantity
        
        # Purchase gifts
        purchased = 0
        for _ in range(max_affordable):
            success = await self.client.send_gift(
                gift_id=gift_id,
                recipient_id=recipient_id,
            )
            
            if success:
                purchased += 1
                balance -= price
                self._daily_spent += price
            else:
                break
        
        # Record in database
        if purchased > 0:
            async with get_session() as session:
                await record_purchase(
                    session=session,
                    gift_id=gift_id,
                    gift_name=gift_name,
                    recipient_id=recipient_id,
                    recipient_username=str(recipient) if isinstance(recipient, str) else None,
                    price=price,
                    quantity=purchased,
                    is_partial=is_partial and purchased < quantity,
                )
            
            GIFTS_PURCHASED.labels(
                gift_name=gift_name,
                recipient=str(recipient),
            ).inc(purchased)
            
            logger.info(
                "purchase_complete",
                gift_id=gift_id,
                gift_name=gift_name,
                recipient=recipient,
                purchased=purchased,
                requested=quantity,
                is_partial=is_partial,
            )
        
        # Record duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        PURCHASE_DURATION.observe(duration)
        
        return PurchaseResult(
            success=purchased > 0,
            purchased_quantity=purchased,
            requested_quantity=quantity,
            is_partial=is_partial and purchased < quantity,
            remaining_balance=balance,
        )
    
    async def _resolve_recipient(self, recipient: str | int) -> int | None:
        """Resolve a username or ID to a user ID.
        
        Args:
            recipient: Username (starting with @) or user ID
            
        Returns:
            User ID or None if not found
        """
        if isinstance(recipient, int):
            return recipient
        
        if isinstance(recipient, str):
            # Remove @ prefix if present
            username = recipient.lstrip("@")
            
            try:
                user = await self.client.client.get_users(username)
                return user.id if user else None
            except Exception as e:
                logger.error("recipient_resolution_failed", username=username, error=str(e))
                return None
        
        return None
    
    def _check_daily_reset(self) -> None:
        """Reset daily spent counter if new day."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        if self._last_reset_date != today:
            self._daily_spent = 0
            self._last_reset_date = today
            logger.info("daily_budget_reset", date=today)

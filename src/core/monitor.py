"""Gift monitoring service."""
import asyncio
from datetime import datetime
from typing import Callable, Any

from src.config import get_settings
from src.observability import get_logger, set_health_status
from src.observability.metrics import (
    GIFTS_CHECKED,
    GIFTS_AVAILABLE,
    CHECK_CYCLE_DURATION,
    ACTIVE_MONITORING,
)
from src.storage import get_session, init_db
from src.storage.database import get_or_create_gift

from .client import TelegramClientWrapper

logger = get_logger(__name__)


class GiftMonitor:
    """Monitors Telegram for new gifts and triggers purchases."""
    
    def __init__(
        self,
        client: TelegramClientWrapper,
        on_new_gift: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        """Initialize the gift monitor.
        
        Args:
            client: Telegram client wrapper
            on_new_gift: Callback for new gift discovery
        """
        self.client = client
        self.on_new_gift = on_new_gift
        
        settings = get_settings()
        self.interval = settings.app.telegram.interval_seconds
        self.gift_config = settings.app.gifts
        
        self._running = False
        self._known_gifts: set[int] = set()
    
    async def start(self) -> None:
        """Start the monitoring loop."""
        logger.info("starting_gift_monitor", interval=self.interval)
        
        # Initialize database
        await init_db()
        set_health_status(database_connected=True)
        
        # Load known gifts from database
        await self._load_known_gifts()
        
        self._running = True
        ACTIVE_MONITORING.set(1)
        
        while self._running:
            try:
                await self._check_cycle()
            except Exception as e:
                logger.error("check_cycle_error", error=str(e))
            
            await asyncio.sleep(self.interval)
    
    async def stop(self) -> None:
        """Stop the monitoring loop."""
        logger.info("stopping_gift_monitor")
        self._running = False
        ACTIVE_MONITORING.set(0)
    
    async def _load_known_gifts(self) -> None:
        """Load known gift IDs from database."""
        from sqlalchemy import select
        from src.storage.models import Gift
        
        async with get_session() as session:
            result = await session.execute(select(Gift.id))
            self._known_gifts = {row[0] for row in result.fetchall()}
        
        logger.info("loaded_known_gifts", count=len(self._known_gifts))
    
    async def _check_cycle(self) -> None:
        """Perform one check cycle."""
        start_time = datetime.utcnow()
        
        # Get available gifts
        gifts = await self.client.get_available_gifts()
        
        if not gifts:
            logger.debug("no_gifts_available")
            return
        
        GIFTS_CHECKED.inc(len(gifts))
        
        # Filter and process gifts
        new_gifts = []
        matching_gifts = []
        
        for gift in gifts:
            gift_id = gift.get("id") or gift.id if hasattr(gift, "id") else None
            if not gift_id:
                continue
            
            # Check if new
            if gift_id not in self._known_gifts:
                new_gifts.append(gift)
                self._known_gifts.add(gift_id)
            
            # Check if matches our criteria
            if self._matches_criteria(gift):
                matching_gifts.append(gift)
        
        # Store new gifts in database
        if new_gifts:
            await self._store_gifts(new_gifts)
            logger.info("new_gifts_discovered", count=len(new_gifts))
        
        # Process matching gifts (sorted by priority)
        if matching_gifts:
            matching_gifts = self._sort_by_priority(matching_gifts)
            
            for gift in matching_gifts:
                if self.on_new_gift:
                    self.on_new_gift(gift)
        
        # Update metrics
        GIFTS_AVAILABLE.set(len(matching_gifts))
        set_health_status(last_check=datetime.utcnow())
        
        # Record cycle duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        CHECK_CYCLE_DURATION.observe(duration)
        
        logger.debug(
            "check_cycle_complete",
            total_gifts=len(gifts),
            new_gifts=len(new_gifts),
            matching_gifts=len(matching_gifts),
            duration_seconds=duration,
        )
    
    def _matches_criteria(self, gift: Any) -> bool:
        """Check if a gift matches our purchase criteria.
        
        Args:
            gift: Gift object from Telegram
            
        Returns:
            True if gift matches criteria
        """
        # Extract gift properties
        gift_id = getattr(gift, "id", gift.get("id") if isinstance(gift, dict) else None)
        price = getattr(gift, "stars", gift.get("stars") if isinstance(gift, dict) else 0)
        total_amount = getattr(gift, "total_amount", gift.get("total_amount") if isinstance(gift, dict) else 0)
        is_limited = getattr(gift, "is_limited", gift.get("is_limited") if isinstance(gift, dict) else False)
        is_sold_out = getattr(gift, "is_sold_out", gift.get("is_sold_out") if isinstance(gift, dict) else False)
        upgrade_price = getattr(gift, "upgrade_stars", gift.get("upgrade_stars") if isinstance(gift, dict) else None)
        
        # Skip sold out
        if is_sold_out:
            return False
        
        # Skip non-limited (optional)
        if not is_limited:
            return False
        
        # Check blacklist
        if gift_id in self.gift_config.blacklist_gifts:
            return False
        
        # Check if matches any range
        for range_config in self.gift_config.ranges:
            if range_config.min_price <= price <= range_config.max_price:
                if total_amount <= range_config.supply_limit:
                    # Check upgradable requirement
                    if range_config.upgradable_only and upgrade_price is None:
                        continue
                    return True
        
        return False
    
    def _sort_by_priority(self, gifts: list[Any]) -> list[Any]:
        """Sort gifts by priority (rarest first).
        
        Args:
            gifts: List of gift objects
            
        Returns:
            Sorted list
        """
        if not self.gift_config.prioritize_low_supply:
            return gifts
        
        def get_total_amount(gift: Any) -> int:
            return getattr(gift, "total_amount", gift.get("total_amount") if isinstance(gift, dict) else float("inf"))
        
        return sorted(gifts, key=get_total_amount)
    
    async def _store_gifts(self, gifts: list[Any]) -> None:
        """Store gifts in the database.
        
        Args:
            gifts: List of gift objects
        """
        async with get_session() as session:
            for gift in gifts:
                gift_data = {
                    "name": getattr(gift, "title", gift.get("title") if isinstance(gift, dict) else "Unknown"),
                    "price": getattr(gift, "stars", gift.get("stars") if isinstance(gift, dict) else 0),
                    "total_amount": getattr(gift, "total_amount", gift.get("total_amount") if isinstance(gift, dict) else 0),
                    "available_amount": getattr(gift, "available_amount", gift.get("available_amount") if isinstance(gift, dict) else 0),
                    "is_limited": getattr(gift, "is_limited", gift.get("is_limited") if isinstance(gift, dict) else False),
                    "is_sold_out": getattr(gift, "is_sold_out", gift.get("is_sold_out") if isinstance(gift, dict) else False),
                    "upgrade_price": getattr(gift, "upgrade_stars", gift.get("upgrade_stars") if isinstance(gift, dict) else None),
                }
                
                gift_id = getattr(gift, "id", gift.get("id") if isinstance(gift, dict) else None)
                if gift_id:
                    await get_or_create_gift(session, gift_id, **gift_data)

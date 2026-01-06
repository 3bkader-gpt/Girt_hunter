"""Telegram notification service."""
from typing import Any

from src.config import get_settings
from src.observability import get_logger

logger = get_logger(__name__)


class NotificationService:
    """Sends notifications to Telegram channel."""
    
    def __init__(self, client: Any) -> None:
        """Initialize the notification service.
        
        Args:
            client: TelegramClientWrapper instance
        """
        self.client = client
        
        settings = get_settings()
        self.channel_id = settings.app.notifications.channel_id
        self.types = settings.app.notifications.types
        self.low_balance_threshold = settings.app.notifications.low_balance_threshold
        self.language = settings.app.language
        
        self._enabled = self.channel_id != -100
    
    async def send_start_message(self) -> None:
        """Send bot startup notification."""
        if not self._enabled:
            return
        
        message = self._format_message(
            "🚀 <b>Gift Hunter Bot Started</b>\n\n"
            "✅ Monitoring for new gifts...\n"
            "📊 Use /stats for statistics"
        )
        
        await self.client.send_message(self.channel_id, message)
    
    async def send_purchase_success(
        self,
        gift_name: str,
        recipient: str | int,
        quantity: int,
        price: int,
        is_partial: bool = False,
    ) -> None:
        """Send purchase success notification."""
        if not self._enabled or not self.types.purchase_success:
            return
        
        emoji = "⚠️" if is_partial else "✅"
        status = "Partial Purchase" if is_partial else "Purchase Success"
        
        message = self._format_message(
            f"{emoji} <b>{status}</b>\n\n"
            f"🎁 Gift: <b>{gift_name}</b>\n"
            f"👤 Recipient: <code>{recipient}</code>\n"
            f"📦 Quantity: {quantity}\n"
            f"💰 Price: {price}⭐ each\n"
            f"💵 Total: {price * quantity}⭐"
        )
        
        await self.client.send_message(self.channel_id, message)
    
    async def send_balance_low(self, balance: int) -> None:
        """Send low balance warning."""
        if not self._enabled or not self.types.balance_low:
            return
        
        if balance > self.low_balance_threshold:
            return
        
        message = self._format_message(
            "⚠️ <b>Low Balance Warning</b>\n\n"
            f"💰 Current Balance: {balance}⭐\n"
            f"📉 Threshold: {self.low_balance_threshold}⭐\n\n"
            "Please top up your balance to continue purchasing."
        )
        
        await self.client.send_message(self.channel_id, message)
    
    async def send_error(self, error_type: str, message: str) -> None:
        """Send error notification."""
        if not self._enabled or not self.types.errors:
            return
        
        notification = self._format_message(
            f"🔴 <b>Error: {error_type}</b>\n\n"
            f"<code>{message}</code>"
        )
        
        await self.client.send_message(self.channel_id, notification)
    
    async def send_daily_summary(
        self,
        gifts_checked: int,
        gifts_purchased: int,
        total_spent: int,
        balance: int,
    ) -> None:
        """Send daily summary notification."""
        if not self._enabled or not self.types.daily_summary:
            return
        
        message = self._format_message(
            "📊 <b>Daily Summary</b>\n\n"
            f"🔍 Gifts Checked: {gifts_checked}\n"
            f"🎁 Gifts Purchased: {gifts_purchased}\n"
            f"💵 Total Spent: {total_spent}⭐\n"
            f"💰 Balance: {balance}⭐"
        )
        
        await self.client.send_message(self.channel_id, message)
    
    def _format_message(self, message: str) -> str:
        """Format message with common elements.
        
        Args:
            message: Raw message
            
        Returns:
            Formatted message with header
        """
        return message

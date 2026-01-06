"""Telegram client wrapper with retry and error handling."""
import asyncio
from typing import Any

from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError

from src.config import get_settings
from src.observability import get_logger, set_health_status
from src.observability.metrics import API_REQUESTS

logger = get_logger(__name__)


class TelegramClientWrapper:
    """Wrapper around Pyrogram client with enhanced error handling."""
    
    def __init__(self) -> None:
        """Initialize the Telegram client."""
        settings = get_settings()
        
        self.client = Client(
            name="gift_hunter_session",
            api_id=settings.telegram.api_id,
            api_hash=settings.telegram.api_hash.get_secret_value(),
            phone_number=settings.telegram.phone_number,
            workdir="data/sessions",
        )
        
        self._connected = False
        self._max_retries = settings.app.telegram.max_retries
        self._retry_delay = settings.app.telegram.retry_delay_seconds
    
    async def start(self) -> None:
        """Start the Telegram client and establish connection."""
        logger.info("starting_telegram_client")
        
        try:
            await self.client.start()
            self._connected = True
            set_health_status(status="healthy", telegram_connected=True)
            
            me = await self.client.get_me()
            logger.info(
                "telegram_connected",
                user_id=me.id,
                username=me.username,
                first_name=me.first_name,
            )
        except Exception as e:
            self._connected = False
            set_health_status(status="unhealthy", telegram_connected=False)
            logger.error("telegram_connection_failed", error=str(e))
            raise
    
    async def stop(self) -> None:
        """Stop the Telegram client gracefully."""
        if self._connected:
            logger.info("stopping_telegram_client")
            await self.client.stop()
            self._connected = False
            set_health_status(telegram_connected=False)
    
    async def __aenter__(self) -> "TelegramClientWrapper":
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.stop()
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected
    
    async def get_available_gifts(self) -> list[Any]:
        """Get list of available gifts from Telegram.
        
        Returns:
            List of gift objects
        """
        API_REQUESTS.labels(method="get_available_gifts").inc()
        
        try:
            # Using raw method call - adjust based on actual Pyrogram API
            result = await self.client.invoke(
                # This is a placeholder - actual method depends on Telegram API
                {"_": "payments.getStarGifts", "hash": 0}
            )
            return result.gifts if hasattr(result, 'gifts') else []
        except FloodWait as e:
            logger.warning("flood_wait", wait_seconds=e.value)
            await asyncio.sleep(e.value)
            return await self.get_available_gifts()
        except RPCError as e:
            logger.error("api_error", error_message=str(e))
            return []
    
    async def get_balance(self) -> int:
        """Get current Telegram Stars balance.
        
        Returns:
            Balance in Stars
        """
        API_REQUESTS.labels(method="get_balance").inc()
        
        try:
            # Placeholder - actual API call depends on Telegram API structure
            result = await self.client.invoke(
                {"_": "payments.getStarsStatus", "peer": {"_": "inputPeerSelf"}}
            )
            return result.balance if hasattr(result, 'balance') else 0
        except RPCError as e:
            logger.error("balance_fetch_failed", error=str(e))
            return 0
    
    async def send_gift(
        self,
        gift_id: int,
        recipient_id: int,
        hide_name: bool = True,
    ) -> bool:
        """Send a gift to a recipient.
        
        Args:
            gift_id: ID of the gift to send
            recipient_id: User ID of the recipient
            hide_name: Whether to hide sender's name
            
        Returns:
            True if successful, False otherwise
        """
        API_REQUESTS.labels(method="send_gift").inc()
        
        for attempt in range(self._max_retries):
            try:
                await self.client.invoke({
                    "_": "payments.sendStarsGift",
                    "gift_id": gift_id,
                    "user_id": recipient_id,
                    "hide_name": hide_name,
                })
                return True
                
            except FloodWait as e:
                logger.warning(
                    "flood_wait_during_purchase",
                    wait_seconds=e.value,
                    attempt=attempt + 1,
                )
                await asyncio.sleep(e.value)
                
            except RPCError as e:
                logger.error(
                    "gift_send_failed",
                    gift_id=gift_id,
                    recipient_id=recipient_id,
                    error=str(e),
                    attempt=attempt + 1,
                )
                
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (2 ** attempt))
                else:
                    return False
        
        return False
    
    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        parse_mode: str = "html",
    ) -> bool:
        """Send a message to a chat.
        
        Args:
            chat_id: Chat ID or username
            text: Message text
            parse_mode: Parse mode (html, markdown)
            
        Returns:
            True if successful
        """
        API_REQUESTS.labels(method="send_message").inc()
        
        try:
            await self.client.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
            )
            return True
        except RPCError as e:
            logger.error("message_send_failed", chat_id=chat_id, error=str(e))
            return False

"""Gift Hunter Bot v2.0 - Main Entry Point."""
import asyncio
import signal
import sys
from functools import partial

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src import __version__
from src.config import get_settings
from src.core import TelegramClientWrapper, GiftMonitor, PurchaseEngine
from src.notifications import NotificationService
from src.observability import (
    setup_logging,
    get_logger,
    start_health_server,
    start_metrics_server,
    set_health_status,
)

console = Console()
logger = get_logger(__name__)


def display_banner() -> None:
    """Display the application banner."""
    banner = Text()
    banner.append("🎁 ", style="bold")
    banner.append("Gift Hunter Bot", style="bold cyan")
    banner.append(f" v{__version__}", style="dim")
    
    panel = Panel(
        banner,
        subtitle="Telegram Gifts Auto-Buyer",
        border_style="cyan",
    )
    console.print(panel)


async def shutdown(signal_received: signal.Signals, monitor: GiftMonitor | None) -> None:
    """Handle graceful shutdown."""
    logger.info("shutdown_signal_received", signal=signal_received.name)
    
    if monitor:
        await monitor.stop()
    
    # Allow tasks to complete
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    
    await asyncio.gather(*tasks, return_exceptions=True)


async def run() -> None:
    """Main application entry point."""
    # Load settings
    try:
        settings = get_settings()
    except Exception as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        sys.exit(1)
    
    # Setup logging
    setup_logging(settings.log_level)
    
    # Display banner
    display_banner()
    
    logger.info(
        "application_starting",
        version=__version__,
        language=settings.app.language,
        interval=settings.app.telegram.interval_seconds,
    )
    
    # Start observability servers
    start_health_server(settings.health_port)
    start_metrics_server(settings.metrics_port)
    logger.info(
        "observability_started",
        health_port=settings.health_port,
        metrics_port=settings.metrics_port,
    )
    
    set_health_status(status="starting")
    
    monitor: GiftMonitor | None = None
    
    try:
        async with TelegramClientWrapper() as client:
            # Initialize services
            purchase_engine = PurchaseEngine(client)
            notification_service = NotificationService(client)
            
            # Create monitor with purchase callback
            async def on_new_gift(gift):
                results = await purchase_engine.process_gift(gift)
                for result in results:
                    if result.success:
                        gift_name = getattr(gift, "title", "Unknown")
                        await notification_service.send_purchase_success(
                            gift_name=gift_name,
                            recipient="Unknown",  # Would need to track this
                            quantity=result.purchased_quantity,
                            price=0,  # Would need to track this
                            is_partial=result.is_partial,
                        )
            
            monitor = GiftMonitor(client, on_new_gift=lambda g: asyncio.create_task(on_new_gift(g)))
            
            # Register signal handlers
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(shutdown(s, monitor)),
                )
            
            # Send start notification
            await notification_service.send_start_message()
            
            # Start monitoring
            await monitor.start()
            
    except KeyboardInterrupt:
        logger.info("keyboard_interrupt")
    except Exception as e:
        logger.error("fatal_error", error=str(e))
        set_health_status(status="unhealthy")
        raise
    finally:
        set_health_status(status="stopped")
        logger.info("application_stopped")


def main() -> None:
    """Entry point for the application."""
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Bot stopped by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

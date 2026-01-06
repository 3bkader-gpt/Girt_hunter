"""Structured logging setup using structlog."""
import logging
import sys
from typing import Any

import structlog


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Determine if we're in a TTY (interactive terminal)
    is_tty = sys.stdout.isatty()
    
    # Shared processors
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    if is_tty:
        # Pretty output for development
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            ),
        ]
    else:
        # JSON output for production/Docker
        processors = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Convenience functions for quick logging
def log_purchase(
    gift_id: int,
    gift_name: str,
    recipient: str | int,
    quantity: int,
    price: int,
    is_partial: bool = False,
) -> None:
    """Log a purchase event with structured data."""
    logger = get_logger("purchase")
    logger.info(
        "gift_purchased",
        gift_id=gift_id,
        gift_name=gift_name,
        recipient=recipient,
        quantity=quantity,
        price=price,
        total_cost=price * quantity,
        is_partial=is_partial,
    )


def log_error(
    error_type: str,
    message: str,
    **extra: Any,
) -> None:
    """Log an error with structured data."""
    logger = get_logger("error")
    logger.error(
        error_type,
        message=message,
        **extra,
    )

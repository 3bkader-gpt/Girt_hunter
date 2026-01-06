"""Async database operations with SQLite."""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Base

# Database configuration
DATA_DIR = Path("data")
DATABASE_PATH = DATA_DIR / "gift_hunter.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize the database and create all tables."""
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session with automatic cleanup."""
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_or_create_gift(session: AsyncSession, gift_id: int, **kwargs) -> tuple:
    """Get existing gift or create a new one.
    
    Returns:
        Tuple of (Gift, created: bool)
    """
    from sqlalchemy import select
    from .models import Gift
    
    stmt = select(Gift).where(Gift.id == gift_id)
    result = await session.execute(stmt)
    gift = result.scalar_one_or_none()
    
    if gift:
        # Update existing gift
        for key, value in kwargs.items():
            if hasattr(gift, key):
                setattr(gift, key, value)
        return gift, False
    else:
        # Create new gift
        gift = Gift(id=gift_id, **kwargs)
        session.add(gift)
        return gift, True


async def record_purchase(
    session: AsyncSession,
    gift_id: int,
    gift_name: str,
    recipient_id: int,
    price: int,
    quantity: int,
    is_partial: bool = False,
    recipient_username: str | None = None,
    transaction_id: str | None = None,
) -> None:
    """Record a purchase in the database."""
    from .models import Purchase
    
    purchase = Purchase(
        gift_id=gift_id,
        gift_name=gift_name,
        recipient_id=recipient_id,
        recipient_username=recipient_username,
        price=price,
        quantity=quantity,
        total_cost=price * quantity,
        is_partial=is_partial,
        transaction_id=transaction_id,
    )
    session.add(purchase)

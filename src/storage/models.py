"""SQLAlchemy models for data persistence."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Gift(Base):
    """Represents a Telegram gift item."""
    
    __tablename__ = "gifts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    available_amount: Mapped[int] = mapped_column(Integer, default=0)
    is_limited: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sold_out: Mapped[bool] = mapped_column(Boolean, default=False)
    upgrade_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    first_seen: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    last_checked: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_gifts_price", "price"),
        Index("ix_gifts_total_amount", "total_amount"),
        Index("ix_gifts_is_limited", "is_limited"),
    )
    
    @property
    def is_upgradable(self) -> bool:
        """Check if gift can be upgraded."""
        return self.upgrade_price is not None
    
    @property
    def availability_percentage(self) -> float:
        """Calculate availability as percentage."""
        if self.total_amount == 0:
            return 0.0
        return (self.available_amount / self.total_amount) * 100
    
    def __repr__(self) -> str:
        return f"<Gift(id={self.id}, name={self.name!r}, price={self.price})>"


class Purchase(Base):
    """Tracks a successful gift purchase."""
    
    __tablename__ = "purchases"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gift_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    gift_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    recipient_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    total_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_partial: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Indexes for analytics
    __table_args__ = (
        Index("ix_purchases_date", "purchased_at"),
        Index("ix_purchases_gift_recipient", "gift_id", "recipient_id"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Purchase(id={self.id}, gift={self.gift_name!r}, "
            f"recipient={self.recipient_id}, qty={self.quantity})>"
        )


class DailyStats(Base):
    """Daily statistics for budget tracking."""
    
    __tablename__ = "daily_stats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)  # YYYY-MM-DD
    total_spent: Mapped[int] = mapped_column(Integer, default=0)
    gifts_purchased: Mapped[int] = mapped_column(Integer, default=0)
    gifts_checked: Mapped[int] = mapped_column(Integer, default=0)
    errors_count: Mapped[int] = mapped_column(Integer, default=0)
    
    def __repr__(self) -> str:
        return f"<DailyStats(date={self.date}, spent={self.total_spent})>"

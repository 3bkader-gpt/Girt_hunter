"""Application settings with Pydantic validation."""
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramSettings(BaseSettings):
    """Telegram API credentials loaded from environment variables."""
    
    model_config = SettingsConfigDict(env_prefix="TELEGRAM_")
    
    api_id: int = Field(..., description="Telegram API ID from my.telegram.org")
    api_hash: SecretStr = Field(..., description="Telegram API Hash")
    phone_number: str = Field(..., description="Phone number with country code")
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Ensure phone number starts with +."""
        if not v.startswith("+"):
            raise ValueError("Phone number must start with + (e.g., +1234567890)")
        return v


class NotificationTypes(BaseModel):
    """Notification type toggles."""
    
    purchase_success: bool = True
    purchase_partial: bool = True
    balance_low: bool = True
    errors: bool = True
    daily_summary: bool = True


class NotificationSettings(BaseModel):
    """Notification configuration."""
    
    channel_id: int = Field(
        default=-100,
        description="Telegram channel ID for notifications (-100 to disable)"
    )
    types: NotificationTypes = Field(default_factory=NotificationTypes)
    low_balance_threshold: int = Field(
        default=1000,
        ge=0,
        description="Balance threshold for low balance alerts"
    )


class GiftRange(BaseModel):
    """Configuration for a gift price range."""
    
    name: str = Field(..., description="Display name for this range")
    min_price: int = Field(default=1, ge=0, description="Minimum price in Stars")
    max_price: int = Field(default=10000, ge=0, description="Maximum price in Stars")
    supply_limit: int = Field(
        default=500000,
        ge=0,
        description="Max total_amount to consider"
    )
    quantity_per_recipient: int = Field(
        default=1,
        ge=1,
        description="Quantity to buy per recipient"
    )
    recipients: list[str | int] = Field(
        default_factory=list,
        description="List of usernames or user IDs"
    )
    upgradable_only: bool = Field(
        default=False,
        description="Only buy upgradable gifts"
    )
    
    @field_validator("max_price")
    @classmethod
    def validate_max_price(cls, v: int, info) -> int:
        """Ensure max_price >= min_price."""
        min_price = info.data.get("min_price", 0)
        if v < min_price:
            raise ValueError(f"max_price ({v}) must be >= min_price ({min_price})")
        return v


class GiftSettings(BaseModel):
    """Gift filtering and priority settings."""
    
    ranges: list[GiftRange] = Field(
        default_factory=list,
        description="List of gift ranges to monitor"
    )
    prioritize_low_supply: bool = Field(
        default=True,
        description="Process rare gifts first"
    )
    blacklist_gifts: list[int] = Field(
        default_factory=list,
        description="Gift IDs to skip"
    )
    blacklist_recipients: list[int] = Field(
        default_factory=list,
        description="User IDs to never send to"
    )


class BudgetSettings(BaseModel):
    """Budget management settings."""
    
    daily_limit: int = Field(
        default=0,
        ge=0,
        description="Max daily spend in Stars (0 = unlimited)"
    )
    reserve_balance: int = Field(
        default=0,
        ge=0,
        description="Minimum balance to always keep"
    )


class TelegramBotSettings(BaseModel):
    """Bot behavior settings."""
    
    interval_seconds: int = Field(
        default=10,
        ge=5,
        description="Polling interval in seconds"
    )
    max_retries: int = Field(
        default=3,
        ge=1,
        description="Max retry attempts per purchase"
    )
    retry_delay_seconds: float = Field(
        default=2.0,
        ge=0.5,
        description="Initial retry delay"
    )


class AppConfig(BaseModel):
    """Non-sensitive application configuration loaded from YAML."""
    
    telegram: TelegramBotSettings = Field(default_factory=TelegramBotSettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    gifts: GiftSettings = Field(default_factory=GiftSettings)
    budget: BudgetSettings = Field(default_factory=BudgetSettings)
    language: Literal["EN", "RU", "AR"] = Field(default="EN")


class Settings(BaseSettings):
    """Main application settings combining env vars and config file."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # From environment variables
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    metrics_port: int = Field(default=9090, ge=1, le=65535)
    health_port: int = Field(default=8080, ge=1, le=65535)
    
    # From config.yaml
    app: AppConfig = Field(default_factory=AppConfig)
    
    @classmethod
    def load_yaml_config(cls, config_path: Path = Path("config.yaml")) -> "Settings":
        """Load settings with YAML config file."""
        settings = cls()
        
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f) or {}
            settings.app = AppConfig(**yaml_config)
        
        return settings


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings.load_yaml_config()

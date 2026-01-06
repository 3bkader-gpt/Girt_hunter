#!/usr/bin/env python3
"""Migrate existing JSON history to SQLite database."""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import init_db, async_session_factory
from src.storage.models import Gift


async def migrate_history() -> None:
    """Migrate history.json to SQLite database."""
    history_file = Path("data/json/history.json")
    
    if not history_file.exists():
        print("ℹ️  No history.json found, skipping migration.")
        return
    
    print("🔄 Starting migration from history.json to SQLite...")
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Load existing history
    try:
        with open(history_file, encoding="utf-8") as f:
            history = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error reading history.json: {e}")
        return
    
    if not history:
        print("ℹ️  history.json is empty, nothing to migrate.")
        return
    
    print(f"📦 Found {len(history)} gifts to migrate")
    
    # Migrate to SQLite
    migrated = 0
    errors = 0
    
    async with async_session_factory() as session:
        for gift_id, gift_data in history.items():
            try:
                gift = Gift(
                    id=int(gift_id),
                    name=gift_data.get("name", gift_data.get("title", "Unknown")),
                    price=gift_data.get("price", gift_data.get("stars", 0)),
                    total_amount=gift_data.get("total_amount", 0),
                    available_amount=gift_data.get("available_amount", 0),
                    is_limited=gift_data.get("is_limited", False),
                    is_sold_out=gift_data.get("is_sold_out", False),
                    upgrade_price=gift_data.get("upgrade_price", gift_data.get("upgrade_stars")),
                    first_seen=datetime.fromisoformat(gift_data["first_seen"]) 
                        if "first_seen" in gift_data else datetime.utcnow(),
                )
                session.add(gift)
                migrated += 1
            except Exception as e:
                print(f"  ⚠️  Error migrating gift {gift_id}: {e}")
                errors += 1
        
        await session.commit()
    
    print(f"\n✅ Migration complete:")
    print(f"   - Migrated: {migrated} gifts")
    print(f"   - Errors: {errors}")
    
    # Backup old file
    if migrated > 0:
        backup_path = history_file.with_suffix(".json.bak")
        history_file.rename(backup_path)
        print(f"   - Backup: {backup_path}")


def main() -> None:
    """Run the migration."""
    print("=" * 50)
    print("Gift Hunter - History Migration Script")
    print("=" * 50)
    print()
    
    asyncio.run(migrate_history())
    
    print()
    print("Migration process finished.")


if __name__ == "__main__":
    main()

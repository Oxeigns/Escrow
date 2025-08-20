from typing import List

from database.mongo import db


async def add_admin(user_id: int) -> None:
    """Add a Telegram user id to the admin list."""
    await db.admins.update_one(
        {"telegram_id": user_id}, {"$set": {"telegram_id": user_id}}, upsert=True
    )


async def remove_admin(user_id: int) -> None:
    """Remove a Telegram user id from the admin list."""
    await db.admins.delete_one({"telegram_id": user_id})


async def list_admins() -> List[int]:
    """Return all admin user ids."""
    cursor = db.admins.find({}, {"_id": 0, "telegram_id": 1})
    return [doc["telegram_id"] async for doc in cursor]

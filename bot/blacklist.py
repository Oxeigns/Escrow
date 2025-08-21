from database.mongo import db


async def is_blacklisted(telegram_id: int):
    doc = await db.blacklist.find_one({"telegram_id": telegram_id, "active": True})
    return bool(doc), doc


async def is_blacklist(telegram_id: int):
    return await is_blacklisted(telegram_id)


async def add_to_blacklist(
    telegram_id: int, reason: str, severity: int = 1, evidence_urls=None
):
    evidence_urls = evidence_urls or []
    await db.blacklist.update_one(
        {"telegram_id": telegram_id},
        {
            "$set": {
                "telegram_id": telegram_id,
                "reason": reason,
                "severity": severity,
                "active": True,
                "evidence_urls": evidence_urls,
            }
        },
        upsert=True,
    )


async def remove_from_blacklist(telegram_id: int):
    await db.blacklist.update_one(
        {"telegram_id": telegram_id}, {"$set": {"active": False}}
    )


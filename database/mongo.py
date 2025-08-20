from motor.motor_asyncio import AsyncIOMotorClient
from bot.config import load_config

_cfg = load_config()
_client = AsyncIOMotorClient(_cfg.MONGO_URL)
db = _client[_cfg.MONGO_DB_NAME]


async def init_indexes():
    await db.users.create_index("telegram_id", unique=True)
    await db.blacklist.create_index("telegram_id", unique=True, sparse=True)
    await db.escrows.create_index("state")

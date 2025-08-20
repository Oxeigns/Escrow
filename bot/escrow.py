from bot.config import load_config
from database.mongo import db
from database.models import EscrowModel
from typing import Optional

_cfg = load_config()


async def create_escrow(payload: dict) -> dict:
    model = EscrowModel(**payload)
    res = await db.escrows.insert_one(model.model_dump())
    return {**model.model_dump(), "_id": str(res.inserted_id)}


async def set_state(escrow_id, state: str):
    await db.escrows.update_one({"_id": escrow_id}, {"$set": {"state": state}})


async def list_escrows(limit: int = 50):
    cur = db.escrows.find().sort("_id", -1).limit(limit)
    return [doc async for doc in cur]

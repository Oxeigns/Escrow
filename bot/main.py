import asyncio
import logging
import sys
from pathlib import Path

try:
    import uvloop
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    uvloop = None

# Ensure project root is on sys.path when running as a script
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from loguru import logger

from bot.config import load_config
from bot.handlers import register_handlers
from bot.callbacks import register_callbacks
from webhooks.handler import run_webhook, delete_webhook
from database.mongo import init_indexes


async def main():
    cfg = load_config()
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Escrow Bot Ultimate")

    bot = Bot(token=cfg.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Register handlers & callbacks
    register_handlers(dp, banner_url=cfg.BANNER_URL)
    register_callbacks(dp)

    async def on_startup(_):
        await init_indexes()
        logger.info("Indexes ensured")

    # Webhook vs Polling
    if cfg.USE_WEBHOOK:
        # run webhook server
        await run_webhook(bot, dp)
    else:
        # ensure webhook is deleted for polling mode
        await delete_webhook(bot)
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == "__main__":
    if uvloop is not None:
        try:
            uvloop.run(main())
        except AttributeError:
            # Fallback if uvloop does not provide run()
            asyncio.run(main())
    else:
        asyncio.run(main())

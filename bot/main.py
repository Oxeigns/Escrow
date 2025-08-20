import sys
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_polling
from loguru import logger

try:
    import uvloop
    uvloop.install()
except ImportError:
    pass

import asyncio

# Set project root for imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from bot.config import load_config
from bot.handlers import register_handlers
from bot.callbacks import register_callbacks
from webhooks.handler import run_webhook, delete_webhook
from database.mongo import init_indexes


def setup_logging():
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add("logs/escrow_bot.log", rotation="1 MB", retention="10 days", level="INFO")


def main():
    setup_logging()
    logger.info("🚀 Starting Escrow Bot Ultimate")

    config = load_config()
    bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Register all handlers
    register_handlers(dp, banner_url=config.BANNER_URL)
    register_callbacks(dp)

    async def on_startup(dispatcher):
        await init_indexes()
        logger.info("✅ MongoDB indexes ensured")
        if not config.USE_WEBHOOK:
            await delete_webhook(bot)
        logger.info("🤖 Bot is ready to receive updates")

    async def on_shutdown(dispatcher):
        await bot.session.close()
        logger.info("🛑 Bot shutdown complete")

    if config.USE_WEBHOOK:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_webhook(bot, dp))
    else:
        start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == "__main__":
    main()

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_polling
from loguru import logger

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from bot.config import load_config
from bot.handlers import register_handlers
from webhooks.handler import run_webhook, delete_webhook
from database.mongo import init_indexes


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger.add("bot.log", rotation="10 MB")


def main():
    cfg = load_config()
    setup_logging()

    bot = Bot(token=cfg.BOT_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers(dp, banner_url=cfg.BANNER_URL)

    async def on_startup(dispatcher: Dispatcher):
        await init_indexes()
        if not cfg.USE_WEBHOOK:
            await delete_webhook(bot)
        logger.info("🚀 Bot started (webhook=%s)", cfg.USE_WEBHOOK)

    async def on_shutdown(dispatcher: Dispatcher):
        await bot.session.close()
        logger.info("🛑 Bot shutdown complete")

    if cfg.USE_WEBHOOK:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_webhook(bot, dp))
    else:
        start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == "__main__":
    main()


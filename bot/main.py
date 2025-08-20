import asyncio
import logging
import uvloop

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
    try:
        uvloop.run(main())
    except AttributeError:
        # Fallback if uvloop not available on platform
        asyncio.run(main())

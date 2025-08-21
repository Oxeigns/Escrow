import logging
import asyncio
import os
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_polling
from loguru import logger

# Ensure project root is in the Python path when executed directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import load_config
from bot.handlers import register_handlers
from webhooks.handler import run_webhook, delete_webhook
from database.mongo import init_indexes


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger.add("logs/escrow_bot.log", rotation="10 MB", retention="14 days")


async def _set_bot_commands(bot: Bot):
    cmds = [
        types.BotCommand("start", "welcome"),
        types.BotCommand("panel", "control panel"),
        types.BotCommand("escrow", "start escrow wizard"),
        types.BotCommand("myescrows", "list your escrows"),
        types.BotCommand("support", "contact support"),
        types.BotCommand("cancel", "cancel current step"),
        types.BotCommand("help", "commands help"),
    ]
    await bot.set_my_commands(cmds)


def main():
    cfg = load_config()
    setup_logging()

    bot = Bot(token=cfg.BOT_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    register_handlers(dp, banner_url=cfg.BANNER_URL)

    async def on_startup(dispatcher: Dispatcher):
        await init_indexes()
        await _set_bot_commands(bot)
        if not cfg.USE_WEBHOOK:
            await delete_webhook(bot)
        logger.info("Bot started (webhook=%s)", cfg.USE_WEBHOOK)

    async def on_shutdown(dispatcher: Dispatcher):
        await bot.session.close()
        logger.info("Shutdown complete")

    if cfg.USE_WEBHOOK:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_webhook(bot, dp))
    else:
        start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == "__main__":
    main()


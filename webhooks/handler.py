from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from bot.config import load_config
from database.mongo import init_indexes

cfg = load_config()


async def on_startup(dp: Dispatcher):
    await init_indexes()


async def on_shutdown(dp: Dispatcher):
    pass


async def run_webhook(bot: Bot, dp: Dispatcher):
    await bot.set_webhook(
        cfg.WEBHOOK_HOST + cfg.WEBHOOK_PATH, drop_pending_updates=True
    )
    await start_webhook(
        dispatcher=dp,
        webhook_path=cfg.WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=cfg.WEBAPP_HOST,
        port=cfg.WEBAPP_PORT,
    )


async def delete_webhook(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)

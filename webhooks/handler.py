from aiogram import Bot, Dispatcher
from aiogram.utils.executor import start_webhook
from bot.config import load_config


def run_webhook(bot: Bot, dp: Dispatcher, *, on_startup, on_shutdown):
    cfg = load_config()

    async def startup(dispatcher):
        await on_startup(dispatcher)
        await bot.set_webhook(
            cfg.WEBHOOK_HOST + cfg.WEBHOOK_PATH, drop_pending_updates=True
        )

    start_webhook(
        dispatcher=dp,
        webhook_path=cfg.WEBHOOK_PATH,
        on_startup=startup,
        on_shutdown=on_shutdown,
        host=cfg.WEBAPP_HOST,
        port=cfg.WEBAPP_PORT,
    )


async def delete_webhook(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)

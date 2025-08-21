from aiogram import types
from bot.buttons import support_buttons
from bot.utils import md2_escape
from bot.config import load_config
from bot.utils_extras import normalize_telegram_url


async def support_message(msg: types.Message, banner_url: str):
    cfg = load_config()
    sup_url = normalize_telegram_url(cfg.SUPPORT_URL)
    text = (
        "Support\n"
        "Need help? Tap a button below or message our admins.\n"
        "Use /dispute and include your Escrow ID if needed."
    )
    kb = support_buttons(sup_url)
    if banner_url:
        try:
            await msg.answer_photo(
                banner_url,
                caption=md2_escape(text),
                parse_mode="MarkdownV2",
                reply_markup=kb,
            )
            return
        except Exception:
            pass
    await msg.answer(md2_escape(text), parse_mode="MarkdownV2", reply_markup=kb)

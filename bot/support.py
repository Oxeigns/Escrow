from aiogram import types
from bot.buttons import support_buttons
from bot.utils import md2_escape
from bot.config import load_config

async def support_message(msg: types.Message, banner_url: str):
    cfg = load_config()
    text = (
        f"*Support Center*\\n"
        f"Need help? Tap a button below or message our admins.\\n\\n"
        f"• For disputes, use /dispute while referencing your Escrow ID.\\n"
    )
    kb = support_buttons(cfg.SUPPORT_URL)
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

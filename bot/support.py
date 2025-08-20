from aiogram import types
from bot.buttons import support_buttons
from bot.utils import md2_escape


async def support_message(msg: types.Message, banner_url: str):
    text = (
        f"*Support Center*\n"
        f"Need help? Tap a button below or message our admins.\n"
        f"\n"
        f"• For disputes, use /dispute while referencing your Escrow ID.\n"
    )
    if banner_url:
        try:
            await msg.answer_photo(
                banner_url,
                caption=md2_escape(text),
                parse_mode="MarkdownV2",
                reply_markup=support_buttons(),
            )
            return
        except:  # fallback to text
            pass
    # Ensure MarkdownV2 safety even in text fallback
    await msg.answer(
        md2_escape(text),
        parse_mode="MarkdownV2",
        reply_markup=support_buttons(),
    )

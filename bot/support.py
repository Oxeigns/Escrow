from aiogram import types
from bot.buttons import support_buttons
from bot.utils import md2_escape


async def support_message(msg: types.Message, banner_url: str):
    """
    Send support information depending on chat type.

    In group chats, the bot reports the group owner's Telegram ID.
    In private chats, it shares the support URL and developer contact.
    """

    # Group chats: show group owner ID
    if msg.chat.type in {"group", "supergroup"}:
        owner_id = "unknown"
        try:
            admins = await msg.bot.get_chat_administrators(msg.chat.id)
            for admin in admins:
                if admin.status == "creator":
                    owner_id = str(admin.user.id)
                    break
        except Exception:
            pass
        text = f"Group owner ID: {owner_id}"
        await msg.answer(md2_escape(text), parse_mode="MarkdownV2")
        return

    # Private chats: provide support links
    text = (
        f"*Support Center*\n"
        f"Need help? Contact our support or developer.\n"
        f"\n"
        f"https://t.me/botdukan\n"
        f"Developer @oxeign\n"
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
        except Exception:  # fallback to text
            pass

    await msg.answer(md2_escape(text), parse_mode="MarkdownV2", reply_markup=support_buttons())

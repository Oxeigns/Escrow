from aiogram import Dispatcher, types
from bot.buttons import main_menu
from bot.support import support_message
from bot.blacklist import is_blacklisted
from bot.utils import md2_escape
from database.mongo import db
from bot.forms import start_form


def register_handlers(dp: Dispatcher, banner_url: str):

    @dp.message_handler(commands=["start"])
    async def start(msg: types.Message):
        txt = (
            "*Escrow Bot Ultimate*\n"
            "\n"
            "💼 Secure peer‑to‑peer trades with escrow.\n"
            "Press 🛡️ Escrow to begin or ℹ️ Help for guidance."
        )
        if banner_url:
            try:
                await msg.answer_photo(
                    banner_url,
                    caption=md2_escape(txt),
                    parse_mode="MarkdownV2",
                    reply_markup=main_menu(),
                )
                return
            except:
                pass
        await msg.answer(
            md2_escape(txt), parse_mode="MarkdownV2", reply_markup=main_menu()
        )

    @dp.message_handler(commands=["support"])
    async def cmd_support(msg: types.Message):
        await support_message(msg, banner_url)

    @dp.message_handler(commands=["help"])
    async def cmd_help(msg: types.Message):
        txt = (
            "*How to use the bot*\n"
            "\n"
            "🛡️ /escrow – start a protected deal\n"
            "🆘 /support – talk to support or view the FAQ\n"
            "⚖️ /dispute – open a dispute with your Escrow ID\n"
        )
        await msg.answer(
            md2_escape(txt), parse_mode="MarkdownV2", reply_markup=main_menu()
        )

    @dp.message_handler(commands=["escrow"])
    async def cmd_escrow(msg: types.Message):
        blacklisted, info = await is_blacklisted(msg.from_user.id)
        if blacklisted:
            reason = info.get("reason", "violation")
            await msg.answer(
                md2_escape(f"⚠️ You are blacklisted. Reason: {reason}"),
                parse_mode="MarkdownV2",
            )
            return
        await db.users.update_one(
            {"telegram_id": msg.from_user.id},
            {
                "$set": {
                    "telegram_id": msg.from_user.id,
                    "username": msg.from_user.username,
                    "full_name": msg.from_user.full_name,
                }
            },
            upsert=True,
        )
        await start_form(msg)

    @dp.message_handler(commands=["dispute"])
    async def cmd_dispute(msg: types.Message):
        await msg.answer(
            md2_escape("Open a dispute by referencing your Escrow ID in the message."),
            parse_mode="MarkdownV2",
        )

    @dp.message_handler()
    async def echo_router(msg: types.Message):
        text = (msg.text or "").lower()
        if "escrow" in text:
            await cmd_escrow(msg)
        elif "support" in text:
            await cmd_support(msg)
        elif "help" in text:
            await cmd_help(msg)
        else:
            await msg.answer(
                md2_escape("Use /escrow to start or /support for help."),
                parse_mode="MarkdownV2",
            )

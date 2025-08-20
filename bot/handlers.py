from aiogram import Dispatcher, types
from bot.buttons import main_menu
from bot.support import support_message
from bot.utils import md2_escape
from bot.admins import add_admin, remove_admin, list_admins
from bot.config import load_config
from bot.wizard import register_wizard
from database.mongo import db


def register_handlers(dp: Dispatcher, banner_url: str):
    cfg = load_config()

    # Wizard
    register_wizard(dp)

    @dp.message_handler(commands=["start"])
    async def cmd_start(msg: types.Message):
        text = (
            "*Escrow Bot Ultimate*\n"
            "Create safe escrow deals in a few guided steps.\n\n"
            "Use /escrow to begin, /help for commands, or /support for assistance."
        )
        if banner_url:
            try:
                await msg.answer_photo(
                    banner_url,
                    caption=md2_escape(text),
                    parse_mode="MarkdownV2",
                    reply_markup=main_menu(),
                )
                return
            except Exception:
                pass
        await msg.answer(md2_escape(text), parse_mode="MarkdownV2", reply_markup=main_menu())

    @dp.message_handler(commands=["help"])
    async def cmd_help(msg: types.Message):
        text = (
            "*Help*\n"
            "• /escrow — start a new escrow\n"
            "• /myescrows — list your escrows\n"
            "• /cancel — cancel the current step\n"
            "• /support — contact support / read FAQ"
        )
        await msg.answer(md2_escape(text), parse_mode="MarkdownV2")

    @dp.message_handler(commands=["support"])
    async def cmd_support(msg: types.Message):
        await support_message(msg, banner_url)

    @dp.message_handler(commands=["myescrows"])
    async def cmd_myescrows(msg: types.Message):
        cur = db.escrows.find(
            {
                "$or": [
                    {"buyer_id": msg.from_user.id},
                    {"seller_id": msg.from_user.id},
                ]
            }
        ).sort("_id", -1).limit(10)
        rows = [r async for r in cur]
        if not rows:
            await msg.answer(md2_escape("No escrows found."), parse_mode="MarkdownV2")
            return
        lines = []
        for r in rows:
            rid = str(r.get("_id"))
            st = r.get("state", "INITIATED")
            amt = int(r.get("amount_cents", 0)) // 100
            cur = r.get("currency", "INR")
            lines.append(f"• {rid} — {st} — {amt} {cur}")
        await msg.answer(md2_escape("*Your Last Escrows:*\n" + "\n".join(lines)), parse_mode="MarkdownV2")

    # Owner-only admin helpers
    @dp.message_handler(commands=["sudo"])
    async def cmd_sudo(msg: types.Message):
        if msg.from_user.id != cfg.OWNER_ID:
            return
        parts = (msg.text or "").split()
        if len(parts) != 2 or not parts[1].isdigit():
            await msg.answer(md2_escape("Usage: /sudo <telegram_id>"), parse_mode="MarkdownV2")
            return
        await add_admin(int(parts[1]))
        await msg.answer(md2_escape("OK: admin added"), parse_mode="MarkdownV2")

    @dp.message_handler(commands=["rmsudo"])
    async def cmd_rmsudo(msg: types.Message):
        if msg.from_user.id != cfg.OWNER_ID:
            return
        parts = (msg.text or "").split()
        if len(parts) != 2 or not parts[1].isdigit():
            await msg.answer(md2_escape("Usage: /rmsudo <telegram_id>"), parse_mode="MarkdownV2")
            return
        await remove_admin(int(parts[1]))
        await msg.answer(md2_escape("OK: admin removed"), parse_mode="MarkdownV2")

    @dp.message_handler(commands=["sudolist"])
    async def cmd_sudolist(msg: types.Message):
        if msg.from_user.id != cfg.OWNER_ID:
            return
        rows = await list_admins()
        if not rows:
            await msg.answer(md2_escape("No admins."), parse_mode="MarkdownV2")
            return
        await msg.answer(md2_escape("Admins:\n" + "\n".join(map(str, rows))), parse_mode="MarkdownV2")

    # Fallback router for keyboard text buttons
    @dp.message_handler()
    async def echo_router(msg: types.Message):
        text = (msg.text or "").lower()
        if "escrow" in text:
            state = dp.current_state(user=msg.from_user.id, chat=msg.chat.id)
            await state.finish()
            for h in dp.message_handlers.handlers:
                if getattr(h, "commands", None) and "escrow" in h.commands:
                    await h.callback(msg)
                    return
        elif "support" in text:
            await cmd_support(msg)
            return
        elif "help" in text:
            await cmd_help(msg)
            return
        else:
            await msg.answer(md2_escape("Use /escrow to start or /support for help."), parse_mode="MarkdownV2")

    @dp.callback_query_handler(lambda c: c.data in {"support_contact", "support_faq"})
    async def cb_support_buttons(cb: types.CallbackQuery):
        if cb.data == "support_contact":
            text = "Support: https://t.me/botdukan\nDeveloper @oxeign"
            await cb.message.answer(md2_escape(text), parse_mode="MarkdownV2")
        else:
            await cb.message.answer(md2_escape("FAQ: https://example.com/faq"), parse_mode="MarkdownV2")
        await cb.answer()


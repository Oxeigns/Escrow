from aiogram import Dispatcher, types
from bot.buttons import main_menu, hero_buttons
from bot.support import support_message
from bot.utils import md2_escape
from bot.config import load_config
from bot.wizard import register_wizard
from database.mongo import db
from bot.utils_extras import normalize_telegram_url


def register_handlers(dp: Dispatcher, banner_url: str):
    cfg = load_config()
    sup_url = normalize_telegram_url(cfg.SUPPORT_URL)

    register_wizard(dp)

    @dp.message_handler(commands=["start"])
    async def cmd_start(msg: types.Message):
        txt = "Welcome to Escrow Bot\nCreate safe escrow deals in a few steps."
        kb_inline = hero_buttons(sup_url, banner_url or "https://t.me")
        if banner_url:
            try:
                await msg.answer_photo(banner_url, caption=md2_escape(txt), parse_mode="MarkdownV2", reply_markup=kb_inline)
                return
            except Exception:
                pass
        await msg.answer(md2_escape(txt), parse_mode="MarkdownV2", reply_markup=kb_inline)

    @dp.message_handler(commands=["panel"])
    async def cmd_panel(msg: types.Message):
        txt = "Control Panel\nUse the buttons below."
        kb_inline = hero_buttons(sup_url, banner_url or "https://t.me")
        if banner_url:
            try:
                await msg.answer_photo(banner_url, caption=md2_escape(txt), parse_mode="MarkdownV2", reply_markup=kb_inline)
                return
            except Exception:
                pass
        await msg.answer(md2_escape(txt), parse_mode="MarkdownV2", reply_markup=kb_inline)

    @dp.message_handler(commands=["help"])
    async def cmd_help(msg: types.Message):
        lines = [
            "/start – welcome",
            "/panel – control panel",
            "/escrow – start a new escrow",
            "/myescrows – list your escrows",
            "/support – contact + FAQ",
            "/cancel – cancel current step",
            "/help – this help",
        ]
        await msg.answer(md2_escape("Commands:\n" + "\n".join(lines)), parse_mode="MarkdownV2", reply_markup=main_menu())

    @dp.message_handler(commands=["support"])
    async def cmd_support(msg: types.Message):
        await support_message(msg, banner_url)

    @dp.message_handler(commands=["myescrows"])
    async def cmd_myescrows(msg: types.Message):
        cur = db.escrows.find({"$or": [{"buyer_id": msg.from_user.id}, {"seller_id": msg.from_user.id}]}).sort("_id", -1).limit(10)
        rows = [r async for r in cur]
        if not rows:
            await msg.answer(md2_escape("No escrows found."), parse_mode="MarkdownV2"); return
        lines = []
        for r in rows:
            rid = str(r.get("_id"))
            st = r.get("state", "INITIATED")
            amt = int(r.get("amount_cents", 0)) // 100
            curc = r.get("currency", "INR")
            lines.append(f"• {rid} — {st} — {amt} {curc}")
        await msg.answer(md2_escape("Recent:\n" + "\n".join(lines)), parse_mode="MarkdownV2")

    @dp.callback_query_handler(lambda c: c.data == "panel_start")
    async def cb_panel_start(cb: types.CallbackQuery):
        await cb.message.answer(md2_escape("Use /escrow to begin."), parse_mode="MarkdownV2")
        await cb.answer()

    @dp.message_handler()
    async def echo_router(msg: types.Message):
        t = (msg.text or "").lower()
        if "escrow" in t:
            for h in dp.message_handlers.handlers:
                if getattr(h, "commands", None) and "escrow" in h.commands:
                    await h.callback(msg); return
        if "support" in t:
            await cmd_support(msg); return
        if "help" in t:
            await cmd_help(msg); return
        if "panel" in t or "control" in t:
            await cmd_panel(msg); return
        await msg.answer(md2_escape("Use /escrow to start or /panel for controls."), parse_mode="MarkdownV2")

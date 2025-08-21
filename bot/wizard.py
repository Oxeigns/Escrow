from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from bot.states import EscrowWizard
from bot.buttons import role_buttons, item_type_buttons, confirm_buttons
from bot.utils import md2_escape
from bot.blacklist import is_blacklist
from bot.escrow import create_escrow


async def _cancel(msg_or_cb, state: FSMContext):
    await state.finish()
    txt = md2_escape("Cancelled.")
    if isinstance(msg_or_cb, types.CallbackQuery):
        try:
            await msg_or_cb.answer()
        except Exception:
            pass
        await msg_or_cb.message.answer(txt, parse_mode="MarkdownV2")
    else:
        await msg_or_cb.answer(txt, parse_mode="MarkdownV2")


def register_wizard(dp: Dispatcher):
    @dp.message_handler(commands=["escrow"])
    async def cmd_escrow(msg: types.Message, state: FSMContext):
        blacklisted, doc = await is_blacklist(msg.from_user.id)
        if blacklisted:
            reason = doc.get("reason", "No reason provided") if doc else "No reason provided"
            await msg.answer(md2_escape(f"Blocked.\nReason: {reason}"), parse_mode="MarkdownV2")
            return
        await msg.answer(md2_escape("Choose role"), parse_mode="MarkdownV2", reply_markup=role_buttons())
        await EscrowWizard.Role.set()

    @dp.callback_query_handler(lambda c: c.data in {"role_buyer", "role_seller"}, state=EscrowWizard.Role)
    async def pick_role(cb: types.CallbackQuery, state: FSMContext):
        role = "buyer" if cb.data.endswith("buyer") else "seller"
        await state.update_data(role=role)
        await cb.answer()
        await cb.message.answer(md2_escape("Enter counterparty @username or ID"), parse_mode="MarkdownV2")
        await EscrowWizard.Counterparty.set()

    @dp.message_handler(state=EscrowWizard.Counterparty, content_types=types.ContentTypes.TEXT)
    async def set_counterparty(msg: types.Message, state: FSMContext):
        cp = (msg.text or "").strip().lstrip("@")
        await state.update_data(counterparty=cp)
        await msg.answer(md2_escape("Item type"), parse_mode="MarkdownV2", reply_markup=item_type_buttons())
        await EscrowWizard.ItemType.set()

    @dp.callback_query_handler(lambda c: c.data.startswith("type_"), state=EscrowWizard.ItemType)
    async def pick_item_type(cb: types.CallbackQuery, state: FSMContext):
        await state.update_data(item_type=cb.data.split("_", 1)[1])
        await cb.answer()
        await cb.message.answer(md2_escape("Short description"), parse_mode="MarkdownV2")
        await EscrowWizard.Description.set()

    @dp.message_handler(state=EscrowWizard.Description, content_types=types.ContentTypes.TEXT)
    async def set_description(msg: types.Message, state: FSMContext):
        desc = (msg.text or "").strip()
        if len(desc) < 5:
            await msg.answer(md2_escape("Please add a bit more detail (≥5 chars)."), parse_mode="MarkdownV2")
            return
        await state.update_data(description=desc)
        await msg.answer(md2_escape("Amount (e.g. `1499` or `1499 USD`)"), parse_mode="MarkdownV2")
        await EscrowWizard.Amount.set()

    @dp.message_handler(state=EscrowWizard.Amount, content_types=types.ContentTypes.TEXT)
    async def set_amount(msg: types.Message, state: FSMContext):
        from bot.states_utils import parse_amount_and_currency
        amount, currency = parse_amount_and_currency(msg.text or "")
        if amount is None or amount <= 0 or amount > 10_000_000:
            await msg.answer(md2_escape("Invalid. Use `1499` or `1499 USD` (INR/USD/EUR)."), parse_mode="MarkdownV2")
            return
        await state.update_data(amount=amount, currency=currency)
        d = await state.get_data()
        summary = (
            f"Confirm\n"
            f"Role: {d['role']}\n"
            f"Counterparty: {d['counterparty']}\n"
            f"Type: {d['item_type']}\n"
            f"Desc: {d['description']}\n"
            f"Amount: {d['amount']} {d['currency']}"
        )
        await msg.answer(md2_escape(summary), parse_mode="MarkdownV2", reply_markup=confirm_buttons())
        await EscrowWizard.Confirm.set()

    @dp.callback_query_handler(lambda c: c.data in {"confirm_yes", "confirm_no"}, state=EscrowWizard.Confirm)
    async def do_confirm(cb: types.CallbackQuery, state: FSMContext):
        if cb.data == "confirm_no":
            await _cancel(cb, state); return

        try:
            await cb.answer("Working…", show_alert=False)
        except Exception:
            pass

        d = await state.get_data()
        role, cp = d["role"], d["counterparty"]
        try:
            counterparty_id = int(cp)
        except Exception:
            counterparty_id = None

        buyer_id = cb.from_user.id if role == "buyer" else (counterparty_id or -1)
        seller_id = (counterparty_id or -1) if role == "buyer" else cb.from_user.id

        payload = {
            "buyer_id": buyer_id,
            "seller_id": seller_id,
            "item_type": d["item_type"],
            "description": d["description"],
            "amount_cents": d["amount"] * 100,
            "currency": d["currency"],
            "state": "PENDING_DEPOSIT",
            "meta": {"created_by": cb.from_user.id, "counterparty_raw": cp},
        }

        try:
            escrow = await create_escrow(payload)
            await state.finish()
            await cb.message.answer(md2_escape(f"Escrow created\nID: {escrow.get('_id','?')}"), parse_mode="MarkdownV2")
        except Exception:
            await cb.message.answer(md2_escape("Could not create escrow. Try again later."), parse_mode="MarkdownV2")

    @dp.callback_query_handler(lambda c: c.data == "wiz_cancel", state="*")
    async def cb_cancel(cb: types.CallbackQuery, state: FSMContext):
        await _cancel(cb, state)

    @dp.message_handler(commands=["cancel"], state="*")
    async def msg_cancel(msg: types.Message, state: FSMContext):
        await _cancel(msg, state)

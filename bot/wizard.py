from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from bot.states import EscrowWizard
from bot.buttons import role_buttons, item_type_buttons, confirm_buttons
from bot.utils import md2_escape
from bot.blacklist import is_blacklisted
from bot.escrow import create_escrow


async def cancel_flow(msg_or_cb, state: FSMContext):
    await state.finish()
    if isinstance(msg_or_cb, types.CallbackQuery):
        await msg_or_cb.message.answer(md2_escape("❌ Cancelled."), parse_mode="MarkdownV2")
        await msg_or_cb.answer()
    else:
        await msg_or_cb.answer(md2_escape("❌ Cancelled."), parse_mode="MarkdownV2")


def register_wizard(dp: Dispatcher):
    @dp.message_handler(commands=["escrow"])
    async def cmd_escrow(msg: types.Message, state: FSMContext):
        # Blacklist check
        blacklisted, doc = await is_blacklisted(msg.from_user.id)
        if blacklisted:
            reason = doc.get("reason", "No reason provided")
            await msg.answer(
                md2_escape(f"🚫 You are blacklisted.\nReason: {reason}"),
                parse_mode="MarkdownV2",
            )
            return
        await msg.answer(
            md2_escape("Are you a Buyer or a Seller?"),
            parse_mode="MarkdownV2",
            reply_markup=role_buttons(),
        )
        await EscrowWizard.Role.set()

    @dp.callback_query_handler(
        lambda c: c.data in {"role_buyer", "role_seller"}, state=EscrowWizard.Role
    )
    async def pick_role(cb: types.CallbackQuery, state: FSMContext):
        role = "buyer" if cb.data.endswith("buyer") else "seller"
        await state.update_data(role=role)
        await cb.message.answer(
            md2_escape("Enter your counterparty's @username or Telegram numeric ID:"),
            parse_mode="MarkdownV2",
        )
        await EscrowWizard.next()
        await cb.answer()

    @dp.message_handler(state=EscrowWizard.Counterparty, content_types=types.ContentTypes.TEXT)
    async def set_counterparty(msg: types.Message, state: FSMContext):
        text = (msg.text or "").strip()
        cp = text.lstrip("@")
        await state.update_data(counterparty=cp)
        await msg.answer(
            md2_escape("Choose item type:"),
            parse_mode="MarkdownV2",
            reply_markup=item_type_buttons(),
        )
        await EscrowWizard.next()

    @dp.callback_query_handler(lambda c: c.data.startswith("type_"), state=EscrowWizard.ItemType)
    async def pick_item_type(cb: types.CallbackQuery, state: FSMContext):
        item_type = cb.data.split("_", 1)[1]
        await state.update_data(item_type=item_type)
        await cb.message.answer(
            md2_escape("Enter a short description of the item/service:"),
            parse_mode="MarkdownV2",
        )
        await EscrowWizard.next()
        await cb.answer()

    @dp.message_handler(state=EscrowWizard.Description, content_types=types.ContentTypes.TEXT)
    async def set_description(msg: types.Message, state: FSMContext):
        desc = (msg.text or "").strip()
        if len(desc) < 5:
            await msg.answer(
                md2_escape("Please provide a slightly longer description (≥ 5 characters)."),
                parse_mode="MarkdownV2",
            )
            return
        await state.update_data(description=desc)
        await msg.answer(
            md2_escape("Enter amount (e.g., `1499`, or `1499 USD`). Default currency is INR."),
            parse_mode="MarkdownV2",
        )
        await EscrowWizard.next()

    @dp.message_handler(state=EscrowWizard.Amount, content_types=types.ContentTypes.TEXT)
    async def set_amount(msg: types.Message, state: FSMContext):
        from bot.states_utils import parse_amount_and_currency

        amount, currency = parse_amount_and_currency(msg.text or "")
        if amount is None:
            await msg.answer(
                md2_escape("Invalid amount. Use `1499` or `1499 USD` (INR/USD/EUR)."),
                parse_mode="MarkdownV2",
            )
            return
        if amount <= 0 or amount > 10_000_000:
            await msg.answer(
                md2_escape("Amount out of range. Enter a positive value under 10,000,000."),
                parse_mode="MarkdownV2",
            )
            return
        await state.update_data(amount=amount, currency=currency)
        data = await state.get_data()
        role = data["role"]
        cp = data["counterparty"]
        item_type = data["item_type"]
        desc = data["description"]
        amt = data["amount"]
        cur = data["currency"]
        summary = (
            f"*Please confirm*\n"
            f"Role: {role}\n"
            f"Counterparty: {cp}\n"
            f"Item type: {item_type}\n"
            f"Description: {desc}\n"
            f"Amount: {amt} {cur}\n"
        )
        await msg.answer(
            md2_escape(summary),
            parse_mode="MarkdownV2",
            reply_markup=confirm_buttons(),
        )
        await EscrowWizard.Confirm.set()

    @dp.callback_query_handler(
        lambda c: c.data in {"confirm_yes", "confirm_no"}, state=EscrowWizard.Confirm
    )
    async def do_confirm(cb: types.CallbackQuery, state: FSMContext):
        if cb.data == "confirm_no":
            await cancel_flow(cb, state)
            return
        data = await state.get_data()
        role = data["role"]
        cp = data["counterparty"]
        try:
            seller_id = int(cp) if role == "buyer" else cb.from_user.id
            buyer_id = cb.from_user.id if role == "buyer" else int(cp)
        except Exception:
            seller_id = cb.from_user.id if role == "seller" else None
            buyer_id = cb.from_user.id if role == "buyer" else None

        payload = {
            "buyer_id": buyer_id,
            "seller_id": seller_id,
            "item_type": data["item_type"],
            "description": data["description"],
            "amount_cents": data["amount"] * 100,
            "currency": data["currency"],
            "state": "PENDING_DEPOSIT",
            "meta": {"created_by": cb.from_user.id, "counterparty_raw": cp},
        }
        escrow = await create_escrow(payload)
        await state.finish()
        await cb.message.answer(
            md2_escape(f"✅ Escrow created.\nID: {escrow.get('_id','?')}"),
            parse_mode="MarkdownV2",
        )
        await cb.answer()

    @dp.callback_query_handler(lambda c: c.data == "wiz_cancel", state="*")
    async def cb_cancel(cb: types.CallbackQuery, state: FSMContext):
        await cancel_flow(cb, state)

    @dp.message_handler(commands=["cancel"], state="*")
    async def msg_cancel(msg: types.Message, state: FSMContext):
        await cancel_flow(msg, state)


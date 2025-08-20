from aiogram import types, Dispatcher
from bot.forms import continue_form_role
from bot.utils import md2_escape
from bot.escrow import create_escrow
from database.mongo import db


def register_callbacks(dp: Dispatcher):

    @dp.callback_query_handler(lambda c: c.data.startswith("role_"))
    async def cb_role(callback: types.CallbackQuery):
        await continue_form_role(callback)

    @dp.callback_query_handler(lambda c: c.data.startswith("confirm_"))
    async def cb_confirm(callback: types.CallbackQuery):
        if callback.data == "confirm_yes":
            # A minimal demo escrow creation with placeholders
            last = await db.users.find_one({"telegram_id": callback.from_user.id})
            role = (last or {}).get("last_role", "buyer")
            payload = {
                "buyer_id": callback.from_user.id if role == "buyer" else 0,
                "seller_id": callback.from_user.id if role == "seller" else 0,
                "item_type": "digital",
                "description": "Auto-created from confirm",
                "amount_cents": 10000,
                "currency": "INR",
                "meta": {"via": "confirm_button"},
            }
            escrow = await create_escrow(payload)
            await callback.message.answer(
                md2_escape(f"✅ Escrow created: {escrow.get('_id','?')}"),
                parse_mode="MarkdownV2",
            )
        elif callback.data == "confirm_no":
            await callback.message.answer(
                md2_escape("❌ Escrow cancelled."), parse_mode="MarkdownV2"
            )

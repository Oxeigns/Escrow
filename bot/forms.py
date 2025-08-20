from aiogram import types
from bot.buttons import role_buttons, confirm_buttons
from bot.utils import md2_escape
from database.mongo import db


async def start_form(msg: types.Message):
    await msg.answer(
        md2_escape("Are you a Buyer or Seller?"),
        parse_mode="MarkdownV2",
        reply_markup=role_buttons(),
    )


async def continue_form_role(callback: types.CallbackQuery):
    role = callback.data.split("_", 1)[1]  # buyer/seller
    await callback.message.answer(
        md2_escape(f"Selected role: {role.title()}\nDescribe the item/service:"),
        parse_mode="MarkdownV2",
    )
    await db.users.update_one(
        {"telegram_id": callback.from_user.id},
        {"$set": {"last_role": role}},
        upsert=True,
    )


async def collect_summary(
    msg: types.Message, role: str, description: str, amount: int, currency: str = "INR"
):
    summary = f"Role: {role}\nDescription: {description}\nAmount: {amount} {currency}\nConfirm?"
    await msg.answer(
        md2_escape(summary), parse_mode="MarkdownV2", reply_markup=confirm_buttons()
    )

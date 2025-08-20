from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("🛡️ Escrow"), KeyboardButton("🆘 Support"))
    kb.add(KeyboardButton("ℹ️ Help"))
    return kb


def role_buttons():
    ik = InlineKeyboardMarkup()
    ik.row(
        InlineKeyboardButton("🛒 Buyer", callback_data="role_buyer"),
        InlineKeyboardButton("🧾 Seller", callback_data="role_seller"),
    )
    ik.add(InlineKeyboardButton("❌ Cancel", callback_data="wiz_cancel"))
    return ik


def item_type_buttons():
    ik = InlineKeyboardMarkup()
    ik.row(
        InlineKeyboardButton("💾 Digital", callback_data="type_digital"),
        InlineKeyboardButton("📦 Physical", callback_data="type_physical"),
        InlineKeyboardButton("🛠 Service", callback_data="type_service"),
    )
    ik.add(InlineKeyboardButton("❌ Cancel", callback_data="wiz_cancel"))
    return ik


def confirm_buttons():
    ik = InlineKeyboardMarkup()
    ik.add(InlineKeyboardButton("✅ Confirm", callback_data="confirm_yes"))
    ik.add(InlineKeyboardButton("❌ Cancel", callback_data="confirm_no"))
    return ik


def support_buttons():
    ik = InlineKeyboardMarkup()
    ik.add(InlineKeyboardButton("📨 Contact Support", callback_data="support_contact"))
    ik.add(InlineKeyboardButton("📜 FAQ", callback_data="support_faq"))
    return ik


from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛡️ Start Escrow (/escrow)"))
    kb.add(KeyboardButton("🆘 Support (/support)"))
    return kb


def role_buttons():
    ik = InlineKeyboardMarkup()
    ik.add(InlineKeyboardButton("🛒 Buyer", callback_data="role_buyer"))
    ik.add(InlineKeyboardButton("💼 Seller", callback_data="role_seller"))
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

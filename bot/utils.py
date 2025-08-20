from loguru import logger
from aiogram import types
import html
import re


def md2_escape(text: str) -> str:
    # Telegram MarkdownV2 reserved characters
    reserved = r"[_*[\]()~`>#+\-=|{}.!]"
    return re.sub(reserved, lambda m: "\\" + m.group(0), text)


def html_escape(text: str) -> str:
    return html.escape(text)


async def safe_reply(message: types.Message, text: str, **kwargs):
    try:
        return await message.answer(text, **kwargs)
    except Exception as e:
        logger.exception("Reply failed: {}", e)


def chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]

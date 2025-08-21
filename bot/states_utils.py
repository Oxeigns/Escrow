import re

ALLOWED_CURRENCIES = {"INR", "USD", "EUR"}


def parse_amount_and_currency(text: str):
    m = re.match(r"^\s*(\d+)(?:\s+([A-Za-z]{3}))?\s*$", (text or "").strip())
    if not m:
        return None, None
    amount = int(m.group(1))
    code = (m.group(2) or "INR").upper()
    if code not in ALLOWED_CURRENCIES:
        return None, None
    return amount, code


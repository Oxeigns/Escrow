def normalize_telegram_url(value: str) -> str:
    v = (value or "").strip()
    if not v:
        return v
    if v.startswith("@"):
        return "https://t.me/" + v.lstrip("@")
    return v

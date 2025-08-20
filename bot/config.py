import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    BOT_TOKEN: str
    OWNER_ID: int
    ADMIN_IDS: list
    BANNER_URL: str
    OWNER_URL: str
    DEVELOPER_URL: str
    SUPPORT_URL: str
    USE_WEBHOOK: bool
    WEBHOOK_HOST: str
    WEBHOOK_PATH: str
    WEBAPP_HOST: str
    WEBAPP_PORT: int
    MONGO_URL: str
    MONGO_DB_NAME: str


def parse_bool(val: str, default=False):
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_config() -> Config:
    return Config(
        BOT_TOKEN=os.getenv("BOT_TOKEN", ""),
        OWNER_ID=int(os.getenv("OWNER_ID", "0")),
        ADMIN_IDS=[
            int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x
        ],
        BANNER_URL="https://graph.org/file/1200bc92e8816982887fe-d272d0fddc2a392fed.jpg",
        OWNER_URL="https://t.me/oxeign",
        DEVELOPER_URL="https://t.me/oxeign",
        SUPPORT_URL="https://t.me/botdukan",
        USE_WEBHOOK=parse_bool(os.getenv("USE_WEBHOOK", "false")),
        WEBHOOK_HOST=os.getenv("WEBHOOK_HOST", ""),
        WEBHOOK_PATH=os.getenv("WEBHOOK_PATH", "/telegram-webhook"),
        WEBAPP_HOST=os.getenv("WEBAPP_HOST", "0.0.0.0"),
        WEBAPP_PORT=int(os.getenv("WEBAPP_PORT", "8080")),
        MONGO_URL=os.getenv("MONGO_URL", "mongodb://localhost:27017"),
        MONGO_DB_NAME=os.getenv("MONGO_DB_NAME", "escrow_bot"),
    )

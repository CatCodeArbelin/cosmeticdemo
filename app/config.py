from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    bot_token: str
    manager_chat_id: int
    database_path: str


def get_settings() -> Settings:
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        manager_chat_id=int(os.getenv("MANAGER_CHAT_ID", "0")),
        database_path=os.getenv("DATABASE_PATH", "demo.db"),
    )

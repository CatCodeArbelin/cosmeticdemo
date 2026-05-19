from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    bot_token: str
    openai_api_key: str
    manager_chat_id: int
    openai_model: str
    database_path: str


def get_settings() -> Settings:
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        manager_chat_id=int(os.getenv("MANAGER_CHAT_ID", "0")),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        database_path=os.getenv("DATABASE_PATH", "demo.db"),
    )

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.ai_service import AIService
from app.bot import create_bot_and_dispatcher
from app.config import get_settings
from app.database import Database
from app.handlers import register_handlers
from app.models import IncomingMessage, IncomingResult
from app.fake_channels import process_incoming_message

settings = get_settings()
db = Database(settings.database_path)
db.init()
ai_service = AIService(settings.openai_api_key, settings.openai_model)
bot, dp = create_bot_and_dispatcher(settings.bot_token)
register_handlers(dp, bot, db, ai_service, settings.manager_chat_id)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # В одном процессе запускаем и API, и polling Telegram-бота.
    bot_task = asyncio.create_task(dp.start_polling(bot))
    yield
    bot_task.cancel()


app = FastAPI(title="Cosmetic Demo Assistant", lifespan=lifespan)


@app.get("/")
async def root():
    return {"ok": True, "service": "cosmetic-demo"}


@app.post("/mock/incoming", response_model=IncomingResult)
async def mock_incoming(payload: IncomingMessage):
    message_id = await process_incoming_message(
        db=db,
        ai_service=ai_service,
        bot=bot,
        manager_chat_id=settings.manager_chat_id,
        source=payload.source,
        client_name=payload.client_name,
        client_message=payload.message,
    )
    return IncomingResult(ok=True, message_id=message_id)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)

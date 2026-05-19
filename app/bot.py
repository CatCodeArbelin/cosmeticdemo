from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


def create_bot_and_dispatcher(token: str):
    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    return bot, dp

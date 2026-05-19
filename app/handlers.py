from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from app.fake_channels import create_demo_max, create_demo_tg, build_manager_card


class ManualReplyState(StatesGroup):
    waiting_text = State()


def register_handlers(dp, bot, db, ai_service, manager_chat_id: int):
    @dp.message(Command("start"))
    async def start_cmd(message: Message):
        await message.answer(
            "AI-помощник менеджера запущен.\n\n"
            "Команды:\n"
            " /demo_max — тестовое сообщение из MAX\n"
            " /demo_tg — тестовое сообщение из Telegram\n"
            " /help — инструкция"
        )

    @dp.message(Command("help"))
    async def help_cmd(message: Message):
        await start_cmd(message)

    @dp.message(Command("demo_max"))
    async def demo_max_cmd(message: Message):
        await create_demo_max(db, ai_service, bot, manager_chat_id)
        await message.answer("Демо-сообщение из MAX отправлено в хаб менеджера.")

    @dp.message(Command("demo_tg"))
    async def demo_tg_cmd(message: Message):
        await create_demo_tg(db, ai_service, bot, manager_chat_id)
        await message.answer("Демо-сообщение из Telegram отправлено в хаб менеджера.")

    @dp.callback_query(F.data.startswith("send"))
    async def send_variant(callback: CallbackQuery):
        action, msg_id = callback.data.split(":")
        msg = db.get_message(int(msg_id))
        if not msg:
            await callback.message.answer("Сообщение не найдено.")
            return
        text = msg["ai_variant_1"] if action == "send1" else msg["ai_variant_2"]
        db.set_status_and_reply(int(msg_id), status="sent", selected_reply=text)
        await callback.message.answer(f"✅ Ответ отправлен клиенту в {msg['source']}:\n{text}")
        await callback.answer()

    @dp.callback_query(F.data.startswith("regen:"))
    async def regenerate(callback: CallbackQuery):
        _, msg_id = callback.data.split(":")
        msg = db.get_message(int(msg_id))
        if not msg:
            await callback.message.answer("Сообщение не найдено.")
            return
        v1, v2 = ai_service.generate_variants(msg["source"], msg["client_name"], msg["client_message"])
        db.update_ai_variants(int(msg_id), v1, v2, status="regenerated")
        text, kb = build_manager_card(int(msg_id), msg["source"], msg["client_name"], msg["client_message"], v1, v2)
        await bot.send_message(chat_id=manager_chat_id, text=text, reply_markup=kb)
        await callback.answer("Сгенерировано заново")

    @dp.callback_query(F.data.startswith("manual:"))
    async def manual_mode(callback: CallbackQuery, state: FSMContext):
        _, msg_id = callback.data.split(":")
        db.set_status_and_reply(int(msg_id), status="manual_pending", selected_reply=None)
        await state.update_data(manual_message_id=int(msg_id))
        await state.set_state(ManualReplyState.waiting_text)
        await callback.message.answer("✍️ Напишите ручной ответ следующим сообщением.")
        await callback.answer()

    @dp.message(ManualReplyState.waiting_text)
    async def manual_reply(message: Message, state: FSMContext):
        data = await state.get_data()
        msg_id = data.get("manual_message_id")
        msg = db.get_message(int(msg_id)) if msg_id else None
        if not msg:
            await message.answer("Сообщение не найдено.")
            await state.clear()
            return
        db.set_status_and_reply(int(msg_id), status="manual_sent", selected_reply=message.text)
        await message.answer(f"✅ Ручной ответ отправлен клиенту в {msg['source']}:\n{message.text}")
        await state.clear()

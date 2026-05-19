from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_manager_card(message_id: int, source: str, client_name: str, client_message: str, v1: str, v2: str):
    text = (
        f"🟣 Новое сообщение из {source}\n\n"
        f"Клиент: {client_name}\n\n"
        f"Сообщение:\n{client_message}\n\n"
        f"AI предлагает:\n\n"
        f"Вариант 1:\n{v1}\n\n"
        f"Вариант 2:\n{v2}"
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отправить 1", callback_data=f"send1:{message_id}")],
            [InlineKeyboardButton(text="✅ Отправить 2", callback_data=f"send2:{message_id}")],
            [InlineKeyboardButton(text="🔄 Сгенерировать заново", callback_data=f"regen:{message_id}")],
            [InlineKeyboardButton(text="✍️ Ответить вручную", callback_data=f"manual:{message_id}")],
        ]
    )
    return text, kb


async def process_incoming_message(db, ai_service, bot, manager_chat_id: int, source: str, client_name: str, client_message: str):
    message_id = db.create_message(source=source, client_name=client_name, client_message=client_message, status="new")
    v1, v2 = ai_service.generate_variants(source=source, client_name=client_name, client_message=client_message)
    db.update_ai_variants(message_id, v1, v2, status="new")
    text, kb = build_manager_card(message_id, source, client_name, client_message, v1, v2)
    await bot.send_message(chat_id=manager_chat_id, text=text, reply_markup=kb)
    return message_id

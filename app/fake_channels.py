from app.services import process_incoming_message


async def create_demo_max(db, ai_service, bot, manager_chat_id: int):
    # Имитация сообщения из MAX для демо.
    return await process_incoming_message(
        db=db,
        ai_service=ai_service,
        bot=bot,
        manager_chat_id=manager_chat_id,
        source="MAX",
        client_name="Анна",
        client_message="Здравствуйте! Нужен уход для сухой кожи 35+, что можете посоветовать?",
    )


async def create_demo_tg(db, ai_service, bot, manager_chat_id: int):
    # Имитация сообщения из Telegram для демо.
    return await process_incoming_message(
        db=db,
        ai_service=ai_service,
        bot=bot,
        manager_chat_id=manager_chat_id,
        source="Telegram",
        client_name="Мария",
        client_message="Добрый день! Есть ли у вас сыворотка для чувствительной кожи?",
    )

# DEMO-прототип AI-помощника менеджера косметического магазина

Это демонстрационный проект (не production), который показывает механику:

**FakeMAX / Telegram → Telegram-хаб менеджера → AI-подсказки → выбор ответа → “отправка” клиенту**.

MAX сейчас имитируется через:
- команду `/demo_max`
- HTTP endpoint `POST /mock/incoming`

## Стек
- Python 3.11+
- aiogram 3
- FastAPI
- OpenAI API
- SQLite
- Docker + docker-compose
- python-dotenv

## Как создать Telegram-бота (BotFather)
1. Откройте Telegram и найдите `@BotFather`.
2. Выполните `/newbot`.
3. Задайте имя и username.
4. Получите токен и сохраните его в `BOT_TOKEN`.

## Как узнать MANAGER_CHAT_ID
1. Запустите бота.
2. Напишите ему любое сообщение.
3. Временный способ: добавьте debug-лог `message.chat.id` в обработчик (или используйте стороннего бота типа userinfobot).
4. Подставьте ID в `MANAGER_CHAT_ID`.

## Настройка `.env`
Скопируйте пример:

```bash
cp .env.example .env
```

Заполните:

```env
BOT_TOKEN=
OPENAI_API_KEY=
MANAGER_CHAT_ID=
OPENAI_MODEL=gpt-4.1-mini
DATABASE_PATH=demo.db
```

## Запуск через Docker
```bash
docker compose up --build
```

Сервис поднимет одновременно:
- FastAPI сервер на `http://localhost:8000`
- aiogram polling-бота

## Тест /demo_max
1. Откройте чат с вашим ботом.
2. Нажмите `/start`.
3. Выполните `/demo_max`.
4. У менеджера появится карточка «Новое сообщение из MAX» и 2 варианта ответа.

## Тест /demo_tg
1. В чате с ботом выполните `/demo_tg`.
2. У менеджера появится карточка «Новое сообщение из Telegram» и 2 варианта ответа.

## Тест webhook-имитации MAX
```bash
curl -X POST http://localhost:8000/mock/incoming \
  -H "Content-Type: application/json" \
  -d '{"source":"MAX","client_name":"Анна","message":"Здравствуйте, нужен уход для сухой кожи"}'
```

Ожидаемый ответ:

```json
{
  "ok": true,
  "message_id": 123
}
```

## Статусы сообщений в SQLite
- `new`
- `sent`
- `regenerated`
- `manual_pending`
- `manual_sent`

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

## Проверка запуска

Проверка выполнена 2026-05-19 (UTC) в текущем окружении репозитория.

### Что было подготовлено
- Создан файл `.env` со значениями:
  - `BOT_TOKEN` (валидный по формату placeholder)
  - `OPENAI_API_KEY` (валидный по формату placeholder)
  - `MANAGER_CHAT_ID` (целое число)

### Команда запуска
```bash
docker compose up --build -d
```

### Фактический результат в этом окружении
- Команда не стартовала, потому что Docker CLI отсутствует:
  - `/bin/bash: line 9: docker: command not found`

### Ожидаемые признаки успеха (когда Docker доступен)
1. **Контейнер успешно собирается**
   - В логах присутствуют шаги `build`/`exporting` без `ERROR`.
   - После старта `docker compose ps` показывает сервис в состоянии `Up`.

2. **FastAPI доступен на `http://localhost:8000/`**
   - Проверка:
     ```bash
     curl http://localhost:8000/
     ```
   - Ожидаемый ответ:
     ```json
     {"ok": true, "service": "cosmetic-demo"}
     ```

3. **Бот стартует polling без падений**
   - В логах есть инициализация polling (`aiogram`) без traceback/exit.
   - Процесс контейнера остаётся в `Up`, не уходит в рестарт.

4. **Проверка `POST /mock/incoming`**
   - Команда из README:
     ```bash
     curl -X POST http://localhost:8000/mock/incoming \
       -H "Content-Type: application/json" \
       -d '{"source":"MAX","client_name":"Анна","message":"Здравствуйте, нужен уход для сухой кожи"}'
     ```
   - Ожидаемый ответ:
     ```json
     {"ok": true, "message_id": 123}
     ```
     где `message_id` — любое целое положительное число.

5. **Сценарий `/demo_max` → карточка → “✅ Отправить 1”**
   - В чате с ботом команда `/demo_max` создаёт карточку менеджеру.
   - Нажатие “✅ Отправить 1” меняет статус сообщения в БД на `sent`.
   - В логах нет ошибок отправки/обработки callback.


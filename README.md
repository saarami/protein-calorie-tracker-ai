# protein-calorie-tracker (Backend)

FastAPI backend for free-text meal tracking (calories + protein), with:
- JWT auth (email+password)
- Analyze+Save meal via OpenAI (Responses API)
- Daily summaries (/today and /days/{date})
- Telegram webhook integration + secure link-code flow
- PostgreSQL + SQLAlchemy + Alembic migrations
- Docker + docker-compose
- Unit tests for services

## Run locally (Docker)
1. Copy `.env.example` to `.env` and fill secrets:
   - `OPENAI_API_KEY`
   - `JWT_SECRET`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_WEBHOOK_SECRET`
2. Start:
```bash
docker compose up --build
```

API will be available on `http://localhost:${API_PORT}` (default 8001).

## Alembic
Migrations run automatically on container start (entrypoint runs `alembic upgrade head`).
To run manually:
```bash
docker compose exec api alembic upgrade head
```

## Telegram webhook
- Endpoint path is `TELEGRAM_WEBHOOK_PATH` (default: `/api/v1/telegram/webhook`)
- Requests must include header `X-Telegram-Secret: <TELEGRAM_WEBHOOK_SECRET>`

## Link flow
1. User registers/logs in.
2. User requests a link code:
   - `POST /api/v1/telegram/link-code` (JWT required)
3. User sends in Telegram:
   - `/link ABC123`
4. Bot links `chat_id` to the user.

## OpenAI model
Default: `gpt-4.1-mini`. You can switch to `gpt-4.1` for higher quality.

## Tests
```bash
docker compose exec api pytest -q
```

# Backend – Protein Calorie Tracker

This directory contains the **backend REST API** for calorie and protein tracking.
It is designed with a clean layered architecture and production-oriented patterns.

This README is intended for developers working on the backend codebase.

---

## Responsibilities

- User authentication & authorization (JWT)
- Meal analysis and persistence
- Daily calorie & protein summaries
- Redis caching for hot paths
- Rate limiting (token bucket)
- Telegram webhook handling

---

## Architecture

- **Routers** – FastAPI endpoints & HTTP orchestration
- **Schemas** – Pydantic models for API contracts
- **Services** – Business logic (meal processing, summaries)
- **Repositories** – Persistence layer
- **Models** – SQLAlchemy ORM entities

---

## Environment Variables

```env
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/db

JWT_SECRET=
JWT_EXPIRES_MINUTES=60

REDIS_URL=redis://redis:6379/0

TELEGRAM_BOT_TOKEN=
TELEGRAM_WEBHOOK_SECRET=
```

---

## Run Backend Only

```bash
docker compose up backend --build
```

API base URL:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## Notes

- Schemas are intentionally separated from ORM models
- Business logic lives exclusively in the service layer
- Repositories are the only layer that interacts with the database

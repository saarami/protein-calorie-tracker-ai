# 🥗 Protein Tracker – Backend REST API

A **production‑grade backend system** for calorie and protein tracking, designed with clean architecture principles, scalability in mind, and modern backend best practices.

This project demonstrates how to build, deploy, and operate a real‑world REST API using Python, FastAPI, cloud infrastructure, CI/CD, and integrations.

---

## 🚀 Features

- **Calorie & Protein Tracking**
  - Free‑text meal input with structured storage
  - Daily summaries and nutritional breakdowns

- **Clean Layered Architecture**
  - Routers → Services → Repositories → Models
  - Clear separation of concerns and testability

- **Authentication & Security**
  - JWT‑based authentication & authorization
  - Secure password hashing
  - Proper HTTP error handling and validation

- **Performance & Reliability**
  - Redis caching for frequently accessed endpoints
  - Token‑bucket rate limiting (IP‑based & extensible to user‑based)
  - Graceful error handling and logging

- **Telegram Integration**
  - Webhook‑based Telegram bot integration
  - Secure webhook secret validation
  - Event‑driven updates

- **DevOps & Infrastructure**
  - Fully containerized with Docker
  - Infrastructure as Code using Terraform
  - Deployed on AWS EC2
  - Secrets managed via AWS SSM Parameter Store

- **CI/CD**
  - Automated testing and deployment with GitHub Actions
  - Zero‑downtime container rebuild & deploy flow

- **Testing & Validation**
  - API tested using Postman collections
  - Environment‑based configuration (local / prod)

---

## 🧱 Architecture Overview

```text
┌───────────────┐
│     Client    │  (Postman / Telegram / Future Frontend)
└───────┬───────┘
        │ HTTP
┌───────▼───────┐
│    Routers    │  (FastAPI endpoints)
│   (Schemas)   │  Request / Response validation
└───────┬───────┘
┌───────▼───────┐
│    Services   │  (Business logic)
└───────┬───────┘
┌───────▼───────┐
│  Repositories │  (Persistence layer)
└───────┬───────┘
┌───────▼───────┐
│     Models    │  (SQLAlchemy ORM)
└───────┬───────┘
┌───────▼───────┐
│    Database   │  (PostgreSQL)
└───────────────┘
```

---

## 🛠 Tech Stack

| Category | Technology |
|--------|------------|
| Language | Python 3.11 |
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Auth | JWT |
| Cache | Redis |
| Rate Limiting | Token Bucket |
| Messaging | Telegram Webhook |
| Containers | Docker / Docker Compose |
| Cloud | AWS EC2 |
| IaC | Terraform |
| CI/CD | GitHub Actions |
| Testing | Postman |

---

## 📁 Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── auth/
│   ├── core/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── infra/
│   │   ├── redis/
│   │   └── telegram/
│   └── main.py
├── tests/
├── Dockerfile
├── docker-compose.yml
└── alembic/
```

---

## 🔐 Environment Variables

All secrets are injected via environment variables or AWS SSM.

Example:

```env
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/db
JWT_SECRET=super-secret-key
JWT_EXPIRES_MINUTES=60

REDIS_URL=redis://redis:6379/0

TELEGRAM_BOT_TOKEN=xxxx
TELEGRAM_WEBHOOK_SECRET=xxxx
```

---

## ▶️ Running Locally

```bash
docker compose up --build
```

API will be available at:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## ☁️ Deployment (AWS)

- EC2 instance provisioned with **Terraform**
- Docker installed via `user_data`
- Secrets pulled from **AWS SSM**
- Containers deployed via **GitHub Actions + AWS SSM RunCommand**

Deployment is fully automated on push to `main`.

---

## 🔄 CI/CD Flow

1. Push to `main`
2. GitHub Actions:
   - Install dependencies
   - Run checks/tests
   - Build Docker images
   - Deploy to EC2 using AWS SSM
3. Containers rebuilt and restarted

---

## 🎯 Why This Project Matters

This project is **not a tutorial app**.

It demonstrates:

- Real backend architecture
- Production‑ready security patterns
- Cloud deployment & automation
- Scalable design decisions
- Clean, maintainable code

Ideal as a **portfolio project for Backend / Platform / DevOps roles**.

---

## 🧩 Future Improvements

- User‑based rate limiting
- Background workers (Celery / RQ)
- Metrics & monitoring (Prometheus)
- Frontend (React / Expo)
- Advanced nutrition analysis

---

## 👤 Author

**Saar Amikam**  
Backend Developer  
Python · FastAPI · Cloud · DevOps  

---

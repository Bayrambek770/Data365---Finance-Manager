# Xisob — Finance Manager

A business finance tracking system for small businesses in Uzbekistan.
Log transactions by voice or text via Telegram, and view analytics on the web dashboard.

---

## What's Inside

| Service | Description |
|---|---|
| **FastAPI Backend** | REST API — transactions, budgets, categories, analytics |
| **Telegram Bot** | Voice & text interface powered by Groq AI |
| **PostgreSQL** | Database for users, transactions, categories, budgets |
| **Frontend** | Web dashboard (React) |

---

## Prerequisites

- Docker & Docker Compose
- A [Groq API key](https://console.groq.com) (free)
- A Telegram Bot token from [@BotFather](https://t.me/BotFather)

---

## Quick Start (Docker)

### 1. Clone the repository

```bash
git clone git@github.com:Bayrambek770/Data365-Finance_manager_backend.git
cd Data365-Finance_manager_backend
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

Then open `.env` and fill in your values:

```env
DATABASE_URL=postgresql://xisob_user:xisob_pass@db:5432/xisob
GROQ_API_KEY=your_groq_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
SECRET_KEY=any_random_secret_string
BACKEND_URL=http://backend:8000
FRONTEND_URL=http://your-server-ip:3000
```

### 3. Start all services

```bash
docker-compose up -d
```

This automatically:
- Starts PostgreSQL
- Runs database migrations (`alembic upgrade head`)
- Seeds default categories
- Starts the backend API on port `8000`
- Starts the Telegram bot
- Starts the frontend on port `3000`

### 4. Check logs

```bash
docker-compose logs -f backend
docker-compose logs -f bot
```

### 5. Open the dashboard

```
http://your-server-ip:3000
```

---

## Local Development (without Docker)

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Create and configure `.env`

```bash
cp .env.example .env
# Edit .env with your values (use localhost URLs)
```

For local development set:
```env
DATABASE_URL=postgresql://xisob_user:xisob_pass_2026@localhost:5432/xisob
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### 3. Set up the database

```bash
createdb xisob
alembic upgrade head
python -m backend.seed
```

### 4. Run the backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Run the bot (separate terminal)

```bash
source .venv/bin/activate
python -m bot.main
```

---

## Telegram Bot Usage

Once the bot is running, find it on Telegram and send `/start`.

| Action | How |
|---|---|
| Register | Send `/start` → choose language → share phone number |
| Log a transaction | Type or send a voice message, e.g. _"Received 500,000 UZS from client"_ |
| Add a category | Tap **➕ Add Category** → choose Income/Expense → enter name |
| View transactions | Tap **📋 My Transactions** |
| Ask a question | _"How much did we spend this month?"_ |
| Edit last transaction | _"Edit last transaction"_ |
| Delete last transaction | _"Delete last transaction"_ |

Supports **Uzbek, Russian, and English** input.

---

## Database Migrations

```bash
# Create a new migration after changing models
alembic revision --autogenerate -m "describe your change"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## API

The backend API is available at `http://localhost:8000`.

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Stopping Services

```bash
# Stop all containers
docker-compose down

# Stop and delete the database volume
docker-compose down -v
```

---

## Rebuild After Code Changes

```bash
docker-compose up -d --build
```

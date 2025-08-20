# Escrow Bot Ultimate

A production-ready Telegram escrow bot with webhook & polling support, MongoDB storage, and an admin CLI.

## Features
- Telegram bot for escrow transactions
- Switchable webhook or long-polling modes
- MongoDB models via Motor
- Admin CLI for managing users and disputes
- Dockerfile and Render deployment config
- Blacklist/scammer detection
- Safe MarkdownV2/HTML rendering

## Requirements
- Python 3.11 (Python 3.12 is not yet supported due to `aiohttp` build issues)

## Installation
### Using pip
```bash
pip install -r requirements.txt
```

### Using Docker
```bash
docker build -t escrow-bot-ultimate .
```

## Local Development
```bash
cp .env.example .env
python bot/main.py
```

## MongoDB Atlas Setup
1. Create a MongoDB Atlas cluster.
2. Whitelist your IP and get the connection string.
3. Update `MONGO_URL` and `MONGO_DB_NAME` in `.env`.

## Admin CLI
```bash
python admin/cli.py --help
```
Use commands like `users`, `transactions`, and `ban` to manage the bot.

## Deployment on Render
1. Push the repository to GitHub.
2. Create a new Web Service on Render and connect the repo.
3. Render will use `render.yaml` for configuration.

See `escrow_bot_codex_instructions.txt` for a quick-start guide.

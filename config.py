"""
Файл конфигурации.

Хранит настройки, например, токен Telegram-бота.
"""
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

GOOGLE_CREDS_PATH = os.getenv("GOOGLE_CREDS_PATH", "credentials.json")
GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден. Проверь .env файл или переменные окружения.")

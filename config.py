"""
Файл конфигурации.

Хранит настройки, например, токен Telegram-бота и параметры для Google OAuth.
"""
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

GOOGLE_CREDS_PATH = os.getenv("GOOGLE_CREDS_PATH", "credentials.json")
GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден. Проверь .env файл или переменные окружения.")

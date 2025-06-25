"""
Файл конфигурации.

Хранит настройки, например, токен Telegram-бота.
"""
from dotenv import load_dotenv

load_dotenv()
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден. Проверь .env файл или переменные окружения.")
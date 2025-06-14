"""
Файл конфигурации.

Хранит настройки, например, токен Telegram-бота.
"""


BOT_TOKEN = '7639182471:AAEgPZ0GEdnGMd7EYlXH0jc7CSUUobXgGZE'

# tg_bot/config.py
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_DIR = os.path.join(BASE_DIR, "tg_bot", "tokens")


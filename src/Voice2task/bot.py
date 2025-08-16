import logging
from telegram import Update
from .config import BOT_TOKEN
from telegram.ext import Application
from .google_calendar_services.main_calendar_setup import MainCalendarSetup


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Bot:
    """
    Класс для создания и настройки Telegram-бота.
    """

    def __init__(self):
        self.main_calendar_setup = MainCalendarSetup()

    def build_bot(self):
        """
        Создает и настраивает экземпляр Telegram-бота.
        """
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен в переменных окружения. Бот не будет работать.")
            raise ValueError("BOT_TOKEN не установлен.")

        app = Application.builder().token(BOT_TOKEN).build()

        return app


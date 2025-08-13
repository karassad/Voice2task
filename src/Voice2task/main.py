import logging
import uvicorn
from telegram.ext import CommandHandler, CallbackQueryHandler
from .bot import Bot
from .server import fastapi_app
from .config import WEBHOOK_URL
from .google_calendar_services.main_calendar_setup import MainCalendarSetup


def main():
    """
        Основная функция для инициализации приложения и запуска сервера.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting Uvicorn Server")

    bot_instance = Bot()
    bot_app = bot_instance.build_bot() #Application

    main_calendar_setup = MainCalendarSetup()

    bot_app.add_handler(CommandHandler("start", bot_instance.start_command))
    bot_app.add_handler(
        CallbackQueryHandler(
            main_calendar_setup.handle_main_calendar_selection,
            pattern=r'^calendar_.*'  # Регулярное выражение для всех кнопок выбора календаря
        )
    )

    fastapi_app.telegram_app_instance = bot_app
    fastapi_app.webhook_url = WEBHOOK_URL

    uvicorn.run(fastapi_app, host='0.0.0.0', port=8000, reload=False, log_level='info')

if __name__ == "__main__":
    main()



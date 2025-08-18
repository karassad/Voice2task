import logging
import uvicorn
from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from src.Voice2task.tg_services.tg_bot_markups.main_menu import send_main_menu
from src.Voice2task.tg_services.main_commands.creating_events.create_event_handler import create_event_command
from src.Voice2task.bot import Bot
from src.Voice2task.server import fastapi_app
from src.Voice2task.config import WEBHOOK_URL
from src.Voice2task.google_services.google_calendar_services.main_calendar_setup import MainCalendarSetup
from src.Voice2task.tg_services.main_commands.start_handler import start_command
from src.Voice2task.tg_services.main_commands.change_calendar_handler import calendar_update_command
from src.Voice2task.tg_services.main_commands.restart_handler import restart_command
from src.Voice2task.ai_services.gemini_parser import GeminiParser

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
    gemini_parser = GeminiParser()

    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("calendar_update", calendar_update_command))
    bot_app.add_handler(CommandHandler('restart', restart_command))

    bot_app.add_handler(
        CallbackQueryHandler(
            restart_command,
            pattern=r'^restart$'
        )
    )

    bot_app.add_handler(
        CallbackQueryHandler(
            main_calendar_setup.handle_main_calendar_selection,
            pattern=r'^calendar_.*'  # Регулярное выражение для всех кнопок выбора календаря
        )
    )

    bot_app.add_handler(ConversationHandler(
        # точка входа в разговор
        entry_points=[
            CommandHandler('create_event', create_event_command),
            CallbackQueryHandler(create_event_command, pattern='^create_event$')
        ],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            'WAITING_FOR_TASK': [MessageHandler(filters.TEXT & ~filters.COMMAND, gemini_parser.parse_user_request)]
        },
        # точка выхода из разговора
        fallbacks=[]
    ))

    fastapi_app.telegram_app_instance = bot_app
    fastapi_app.webhook_url = WEBHOOK_URL

    uvicorn.run(fastapi_app, host='0.0.0.0', port=8000, reload=False, log_level='info')

if __name__ == "__main__":
    main()



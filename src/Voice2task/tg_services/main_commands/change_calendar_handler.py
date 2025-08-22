import logging
from telegram import Update
from telegram.ext import ContextTypes
from src.Voice2task.google_services.google_calendar_services.main_calendar_setup import MainCalendarSetup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def calendar_update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает команду /calendar_update.
    Начинает процесс смены календаря пользователя.
    """
    if update.callback_query:
        await update.callback_query.answer()

    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    logger.info(f"Received /calendar_update command from user {user_id} ({user_name})")

    try:
        main_calendar_setup = MainCalendarSetup()
        await main_calendar_setup.start_calendar_selection_flow(update, context)
        logger.info(f"Started calendar selection flow for user {user_id}.")

    except Exception as e:
        logger.error(f"Error starting calendar selection flow for user {user_id}: {e}", exc_info=True)

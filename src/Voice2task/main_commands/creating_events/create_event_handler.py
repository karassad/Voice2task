import logging
from ...google_calendar_services.main_calendar_setup import MainCalendarSetup
from telegram import Update
from telegram.ext import ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_event_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Обрабатывает команду /create_event.
    :param update:
    :param context:
    :return:
    '''
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    logger.info(f"Received /create_event command from user {user_id} ({user_name})")

    # try:
    #     main_calendar_setup = MainCalendarSetup()
    #     if check_is_main
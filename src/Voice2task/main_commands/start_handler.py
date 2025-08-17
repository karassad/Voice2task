import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..message_utils.message_send_logic import send_new_message
from ..handlers.oauth_handler import OauthHandler
from ..google_calendar_services.main_calendar_setup import MainCalendarSetup
from ..tg_bot_markups.main_menu import send_main_menu
from ..db_services.user_storage import UserStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает команду /start.
    проверяет, авторизован ли пользователь, и направляет его в соответствующий поток
    """
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    logger.info(f"Received /start command from user {user_id} ({user_name})")

    try:
        # авторизация
        await send_new_message(update, context, f'Привет, {user_name}!')
        logger.info(f"User {user_id} started the bot.")

        us = UserStorage()
        token = await us.get_user_token(user_id)

        if token:
            logger.info(f"User {user_id} is authorized with token: {token}")
            logger.info(f"User {user_id} is already authorized ")

            await send_main_menu(context.bot, update.effective_chat.id, update)

        else:
            logger.info(f"User {user_id} is not authorized. Starting OAuth process.")
            oauthHandler = OauthHandler()
            await oauthHandler.user_auth_process(user_id, update, context)

        # main_calendar_setup = MainCalendarSetup()
        # if await main_calendar_setup.check_is_main_calendar_set(str(user_id)):
        #     logger.info(f"Main calendar is already set for user {user_id}.")
        #     await send_main_menu(context.bot, update.effective_chat.id, update)
        # else:
        #     try:
        #         logger.info(f"Main calendar is not set for user {user_id}. Starting calendar selection flow.")
        #         await main_calendar_setup.start_calendar_selection_flow(update, context)
        #     except Exception as e:
        #         logger.error(f"Error starting calendar selection flow for user {user_id}: {e}", exc_info=True)


    except Exception as e:
        logger.error(f"Error sending start message to user {user_id}: {e}", exc_info=True)

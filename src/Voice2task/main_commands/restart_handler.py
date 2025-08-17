import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..main_commands.start_handler import start_command
from ..db_services.user_storage import UserStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Обрабатывает команду /restart.
    :param update:
    :param context:
    :return:
    '''
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    logger.info(f"Received /restart command from user {user_id} ({user_name})")


    try:
        #удаляем данные пользователя из бд
        logger.info('start delete data')
        us = UserStorage()
        await us.delete_all_user_data(user_id)

        try:
            logger.info('start start command')
            await start_command(update, context)
        except Exception as e:
            logger.error(f"Error during start command after restart for user {user_id}: {e}", exc_info=True)


    except Exception as e:
        logger.error(f"Error deleting user data for {user_id}: {e}", exc_info=True)





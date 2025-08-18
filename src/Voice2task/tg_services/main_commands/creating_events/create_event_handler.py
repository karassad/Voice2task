import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ....tg_services.message_utils.message_scripts import CREATE_TASK_INSTRUCTIONS
from ....tg_services.message_utils.message_send_logic import send_new_message


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WAITING_FOR_TASK = 0

async def create_event_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Обрабатывает команду /create_event.
    :param update:
    :param context:
    :return:
    '''
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    logger.info(f"Received /create_event command from user {user_id} ({user_name})")

    try:
        await send_new_message(update, context, CREATE_TASK_INSTRUCTIONS)
        return 'WAITING_FOR_TASK'
    except Exception as e:
        logger.error(f"Error sending create event instructions to user {user_id}: {e}", exc_info=True)
        return ConversationHandler.END

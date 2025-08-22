import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ....tg_services.message_utils.message_scripts import CREATE_MEET_INSTRUCTIONS
from ....tg_services.message_utils.message_send_logic import edit_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_google_meet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Обрабатывает команду /create_google_meet.
    :param update:
    :param context:
    :return:
    '''

    if update.callback_query:
        await update.callback_query.answer()

    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    logger.info(f"Received /create_google_meet command from user {user_id} ({user_name})")

    try:
        #этот параметр словит ии, чтобы создать внутри json файла блок,
        # необходимый для создания созвона
        context.user_data['google_meet_block'] = True

        await edit_message(update, context, CREATE_MEET_INSTRUCTIONS)
        return 'WAITING_FOR_TASK'
    except Exception as e:
        logger.error(f"Error sending create google_meet instructions to user {user_id}: {e}", exc_info=True)
        return ConversationHandler.END

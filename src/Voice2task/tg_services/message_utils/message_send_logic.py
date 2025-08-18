import logging

from telegram import Update
from telegram.ext import ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_new_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None):
    '''
    Отправляет новое сообщение в чат.
    Сохраняет message_id отправленного сообщения в user_data для последующего редактирования.
    '''
    chat_id = update.effective_chat.id
    try:
        message = await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup
        )
        context.user_data['last_message_id'] = message.message_id
        # context.user_data['last_message'] = last_message
        # return last_message #true or false

    except Exception as e:
        logger.error(f"Не удалось отправить сообщение в чат {chat_id}: {e}")

async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None):
    '''
    Редактирует последнее сообщение бота в чате.
    Использует message_id из user_data для редактирования.
    '''
    chat_id = update.effective_chat.id
    last_message_id = context.user_data.get('last_message_id')

    if not last_message_id:
        logger.warning(
            f"Не найден message_id для редактирования в чате {chat_id}. Запускаем отправку нового сообщения.")
        return await send_new_message(update, context, text, reply_markup)

    try:
        message = await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text=text,
            reply_markup=reply_markup
        )
        context.user_data['last_message_id'] = message.message_id
        # context.user_data['last_message'] = last_message
  #true or false
    except Exception as e:
        logger.error(f"Не удалось отредактировать сообщение {last_message_id} в чате {chat_id}: {e}")
        # Если редактирование не удалось, отправляем новое сообщение
        return await send_new_message(update, context, text, reply_markup)

async def send_smart_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, last_message: bool, reply_markup=None):
    """
    Отправляет новое сообщение или редактирует последнее сообщение бота в чате.
    Сохраняет message_id последнего сообщения бота в user_data.
    """
    # last_message = context.user_data.get('last_message', True)
    if not last_message:
        await send_new_message(update, context, text, reply_markup)
    else:
        await edit_message(update, context, text, last_message)




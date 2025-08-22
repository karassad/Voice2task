
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot, Update
from telegram.ext import ContextTypes

from src.Voice2task.tg_services.message_utils.message_send_logic import edit_message, send_new_message
from src.Voice2task.db_services.user_storage import UserStorage
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, like_new_message: True):

    user_storage = UserStorage()
    calendar_data = await user_storage.get_main_calendar(int(update.effective_user.id))
    logger.info(f"Получение основного календаря для пользователя {update.effective_user.id}: {calendar_data}")
    calendar_name = calendar_data.get('name') if calendar_data else None
    logger.info(f"Основной календарь для пользователя {update.effective_user.id}: {calendar_name}")

    buttons = [
        [InlineKeyboardButton("📝 Создать задачу", callback_data="create_event")],
        [InlineKeyboardButton("📞 Создать созвон (Google Meet)", callback_data="create_google_meet")],
        [InlineKeyboardButton("📅 Сменить календарь", callback_data="calendar_update")],
        [InlineKeyboardButton("🔄 Рестарт бота (повторная авторизация)", callback_data="restart")],
    ]
    markup = InlineKeyboardMarkup(buttons)

    calendar_text = (
        f"<b>{calendar_name}</b>" if calendar_name else "<b>не выбран</b>"
    )

    if like_new_message:

        await send_new_message(
            update,
            context,
            text=f"Сейчас Ваш текущий основной календарь: {calendar_text}.",
            parse_mode="HTML",
            reply_markup=markup
        )

    else:

        await edit_message(
            update,
            context,
            text=f"Сейчас Ваш текущий основной календарь: {calendar_text}.",
            parse_mode="HTML",
            reply_markup=markup
        )

    logger.info('отправлено меню')

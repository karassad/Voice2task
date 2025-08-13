import logging
from telegram import Update
from .config import BOT_TOKEN
from telegram.ext import Application, ContextTypes

from .message_utils.message_send_logic import send_new_message
from .tg_bot_markups.main_menu import send_main_menu
from .google_calendar_services.main_calendar_setup import MainCalendarSetup
from .handlers.oauth_handler import OauthHandler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Bot:
    """
    Класс для создания и настройки Telegram-бота.
    """

    def __init__(self):
        self.main_calendar_setup = MainCalendarSetup()

    def build_bot(self):
        """
        Создает и настраивает экземпляр Telegram-бота.
        """
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен в переменных окружения. Бот не будет работать.")
            raise ValueError("BOT_TOKEN не установлен.")

        app = Application.builder().token(BOT_TOKEN).build()

        return app

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает команду /start.
        Отправляет приветственное сообщение пользователю.
        """
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        logger.info(f"Received /start command from user {user_id} ({user_name})")
        # context.user_data['last_message'] = True

        try:
            #авторизация
            await send_new_message(update, context, f'Привет, {user_name}!')
            logger.info(f"User {user_id} started the bot.")
            oauthHandler = OauthHandler()
            await oauthHandler.user_auth_process(str(user_id), update)

            #выбор календаря
            #если календарь выбран, отправляем главное меню
            if await self.main_calendar_setup.check_is_main_calendar_set(user_id=str(user_id)):
                await send_main_menu(context.bot, update.effective_chat.id, update)

            #если календарь не установлен, запускаем процесс выбора календаря
            else:
                try:
                    await self.main_calendar_setup.start_calendar_selection_flow(update, context)
                    logger.info(f"Started calendar selection flow for user {user_id}.")

                except Exception as e:
                    logger.error(f"Error starting calendar selection flow for user {user_id}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Error sending start message to user {user_id}: {e}", exc_info=True)



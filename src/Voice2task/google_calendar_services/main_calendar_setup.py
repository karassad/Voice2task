import logging
from calendar import calendar

from telegram import Update

from ..db_services.user_storage import UserStorage
from ..google_calendar_services.calendar_service import CalendarService
from telegram.ext import ContextTypes

from ..message_utils.message_send_logic import edit_message
from ..tg_bot_markups.main_menu import send_main_menu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainCalendarSetup:
    """
    Сервис для работы с основным календарем пользователя.
    """

    def __init__(self):
        self.user_storage = UserStorage()
        self.calendar_service = CalendarService()

    async def start_calendar_selection_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
            Запускает процесс выбора основного календаря. (запускает make_list_calendar_buttons из CalendarService)
            Получает список календарей и отправляет пользователю кнопки.
        """
        user_id = update.effective_user.id
        try:
            logger.info(f"Запуск процесса выбора основного календаря для пользователя {user_id}.")
            await self.calendar_service.make_list_calendar_buttons(str(user_id), update, context)
        except Exception as e:
            logger.error(f"Ошибка при запуске процесса выбора календаря для пользователя {user_id}: {e}", exc_info=True)

    async def check_is_main_calendar_set(self, user_id: str):
        """
        Проверяет, установлен ли основной календарь для пользователя.
        :return: True, если календарь установлен, иначе False.
        """
        try:
            calendar_status = await self.user_storage.get_main_calendar(int(user_id))
            logger.info(f"Проверка основного календаря для пользователя {user_id}: {calendar_status}")
            if not calendar_status:
                #логика выбора календаря
                return None
            else:
                return True
        except Exception as e:
            logger.error(f"Ошибка при проверке основного календаря: {e}", exc_info=True)
            return False

    async def handle_main_calendar_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''
        Обрабатывает выбор основного календаря пользователем из update.callback_query
        '''

        try:
            user_id = int(update.effective_user.id)
            query = update.callback_query
            await query.answer()

            callback_data = query.data
            if not callback_data.startswith('calendar_'):
                # Это не наш callback, выходим
                return
            logger.info(f"Пользователь {user_id} выбрал календарь: {callback_data}")

            try:
                hashed_cal_id = callback_data.replace('calendar_', '')
                orig_cal_id = context.user_data.get(f'calendar_hash_{hashed_cal_id}')

                if not orig_cal_id:
                    logger.error(f"Не найден оригинальный ID календаря для хеша {hashed_cal_id} у пользователя {user_id}.")
                    return

                await self.user_storage.update_user_data(user_id, {'calendar': orig_cal_id})
                # await context.bot.send_message(
                #     chat_id=user_id,
                #     text=f"Выбран календарь: {orig_cal_id}. Теперь вы можете создавать события в этом календаре."
                # )
                await edit_message(update, context, text=f"Выбран календарь: {orig_cal_id}. Теперь вы можете создавать события в этом календаре.")
                del context.user_data[f'calendar_hash_{hashed_cal_id}']

                await send_main_menu(context.bot, update.effective_chat.id, update)

            except Exception as e:
                logger.error(f"Ошибка при обработке выбора календаря: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Ошибка при обработке выбора календаря: {e}", exc_info=True)






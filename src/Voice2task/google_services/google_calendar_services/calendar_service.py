import hashlib
import logging

from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from google.auth.aio.credentials import Credentials
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from src.Voice2task.config import SCOPES
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from telegram.ext import ContextTypes

from src.Voice2task.db_services.user_storage import UserStorage
from src.Voice2task.tg_services.message_utils.message_send_logic import edit_message, send_new_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalendarService:
    """
        Класс для создания сервиса Google Calendar. Методы для работы с календарями
    """
    def __init__(self):
        self.user_storage = UserStorage()

    async def create_calendar_service(self, user_id: str):
        """
        Метод для получения аутентифицированного сервиса Google Calendar.
        Инкапсулирует логику получения учетных данных и создания объекта CalendarService.
        :param user_id: ID пользователя.
        :return: Экземпляр CalendarService или None, если пользователь не авторизован.
        """
        try:
            credentials_dict = await self.user_storage.get_user_data(int(user_id))
            logger.info(f"Получены учетные данные для пользователя {user_id}: {credentials_dict}")

            if not credentials_dict:
                logger.warning(f"Пользователь {user_id} не авторизован в Google Calendar.")
                return None

            try:
                #cоздаем объект Credentials из словаря - с помощью него потом создаем сервис для работы с календарем
                creds_object = Credentials.from_authorized_user_info(credentials_dict, SCOPES)

                if creds_object.expired and creds_object.refresh_token:
                    logger.info(f"Обновление токена для пользователя {user_id}.")
                    try:
                        creds_object.refresh(Request())
                        logger.info(f"Обновление токена завершено. Статус валидности токена: {creds_object.valid}")

                        if creds_object.valid:
                            updated_credentials_dict = {
                                'token': creds_object.token,
                                'refresh_token': creds_object.refresh_token,
                                'token_uri': creds_object.token_uri,
                                'client_id': creds_object.client_id,
                                'client_secret': creds_object.client_secret,
                                'scopes': creds_object.scopes
                            }
                            await self.user_storage.update_user_data(int(user_id), updated_credentials_dict)
                        else:
                            raise ValueError("Токен невалиден после попытки обновления.")
                    except RefreshError as e:
                        logger.error(f"Ошибка RefreshError при обновлении токена для пользователя {user_id}: {e}",
                                     exc_info=True)
                        return None
                    except Exception as e:
                        # Ловим другие возможные ошибки при обновлении
                        logger.error(f"Неожиданная ошибка при обновлении токена для пользователя {user_id}: {e}",
                                     exc_info=True)
                        return None

                # Если после обновления токенов все еще нет, это ошибка
                if not creds_object or not creds_object.valid:
                    raise ValueError("Не удалось обновить токен авторизации.")

                calendar_service = build('calendar', 'v3', credentials=creds_object)
                logger.info(f"Успешно создан сервис календаря для пользователя {user_id}")
                return calendar_service

            except ValueError as e:
                logger.error(f"Ошибка при создании объекта Credentials для пользователя {user_id}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Ошибка при создании сервиса календаря для пользователя {user_id}: {e}", exc_info=True)
            return None

    async def get_calendars_list(self, user_id: str):
        calendar_service = await self.create_calendar_service(user_id)
        if not calendar_service:
            logger.error(f"Не удалось создать сервис календаря для пользователя {user_id}.")

        calendar_list = calendar_service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        return calendars

    async def make_list_calendar_buttons(self, user_id: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Создает кнопки со всеми календарями пользователя
        :param user_id: ID пользователя.
        :return: inline кнопки для выбора календаря.
        """
        try:
            calendar_list = await self.get_calendars_list(user_id)
            if not calendar_list:
                logger.info(f"Пользователь {user_id} не имеет доступных календарей.")
                return None

            buttons = []
            for calendar in calendar_list:
                calendar_id = calendar.get('id')
                hashed_cal_id = hashlib.sha256(calendar_id.encode('utf-8')).hexdigest()[:16] #хэшированный ID календаря

                if context.user_data is None:
                    context.user_data = {}

                context.user_data[f'calendar_hash_{hashed_cal_id}'] = {
                    'id': calendar_id,
                    'summary': calendar.get('summary')
                }
                buttons.append([InlineKeyboardButton(calendar['summary'], callback_data=f'calendar_{hashed_cal_id}')])
                logger.info(f"Добавлена кнопка для календаря: {calendar['summary']} (ID: {calendar_id}), хэш: {hashed_cal_id}")
            keyboard = InlineKeyboardMarkup(buttons)

            if update.callback_query:
                await edit_message(update, context, text="Выберите календарь:",
                                   reply_markup=keyboard)
            else:
                 await send_new_message(update, context, text="Выберите календарь:",
                                        reply_markup=keyboard)


        except Exception as e:
            logger.error(f"Ошибка при получении списка календарей для пользователя {user_id}: {e}", exc_info=True)




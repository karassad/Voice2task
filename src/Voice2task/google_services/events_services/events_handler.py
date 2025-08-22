import json
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.Voice2task.tg_services.tg_bot_markups.main_menu import send_main_menu
from src.Voice2task.tg_services.message_utils.message_scripts import MEET_CREATED, EVENT_CREATED
from src.Voice2task.db_services.user_storage import UserStorage
from src.Voice2task.tg_services.message_utils.message_send_logic import send_new_message
from src.Voice2task.google_services.google_calendar_services.calendar_service import CalendarService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventsHandler:
    '''
    Класс для различных действий с событиями в календаре
    '''

    def __init__(self):
        self.calendar_service = CalendarService()
        self.user_storage = UserStorage()

    async def create_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE, event_body_json: str):
        '''
        Создает событие в гугл календаре на основе json-объекта
        :param update:
        :param context:
        :param event_body_json
        :return:
        '''


        user_id = update.effective_user.id
        logger.info(f"start creating event for user {user_id}")

        try:
            #парсим из строки в словарь
            event_body = json.loads(event_body_json)

            # Получаем учетные данные и ID календаря из контекста
            credentials_data = await self.user_storage.get_user_token(user_id)



            # credentials_data = json.loads(credentials_json)
            context.user_data['token'] = credentials_data  # Кэшируем токен в контекст (ускорит последующие вызовы)

            main_calendar = await self.user_storage.get_main_calendar(user_id)
            logger.info(main_calendar)
            main_calendar_id = main_calendar['id']

            logger.info(f'credentials data from context: {credentials_data}, calendar: {main_calendar_id}')

            # credentials = Credentials(**credentials_data)

            calendar_service = await self.calendar_service.create_calendar_service(str(user_id))

            request = calendar_service.events().insert(
                calendarId=main_calendar_id,
                body=event_body,
                conferenceDataVersion=1 if 'conferenceData' in event_body else 0
            )

            event = request.execute()

            # Отправляем пользователю подтверждение
            event_link = event.get('htmlLink')
            summary = event_body.get('summary', 'Событие')

            if 'conferenceData' in event_body:
                confirmation_message = MEET_CREATED.format(summary=summary, link=event_link)
            else:
                confirmation_message = EVENT_CREATED.format(summary=summary, link=event_link)

            await send_new_message(update, context, confirmation_message, parse_mode=ParseMode.HTML)

            await send_main_menu(update, context, True)


        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error creating calendar event for user {user_id}: {e}", exc_info=True)


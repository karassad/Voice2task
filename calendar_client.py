import os
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from tg_bot.config import TOKENS_DIR

# настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendar:

    def __init__(self, user_id: int):
        self.token_path = os.path.join(TOKENS_DIR, f"token_{user_id}.json")
        if not os.path.exists(self.token_path):
            logger.error(f"Файл токена не найден: {self.token_path}")
            raise FileNotFoundError(f"Пользователь {user_id} не авторизован")

        logger.info(f"Загружаем токен из: {self.token_path}")
        self.credentials = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        self.service = build('calendar', 'v3', credentials=self.credentials)
        logger.info("Сервис Google Calendar инициализирован")

    def get_calendar_list(self):
        logger.info("Получаем список календарей пользователя")
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id: str, body: dict):
        logger.info(f"Добавляем событие в календарь {calendar_id}")
        return self.service.events().insert(calendarId=calendar_id, body=body).execute()

    def add_event_to_primary(self, calendar_id, body):
        logger.info("Добавляем событие в основной календарь")
        return self.service.events().insert(calendarId='primary', body=body).execute()


# obj = GoogleCalendar()
# calendar = 'kladmoy04@mail.ru'
# pprint.pprint(obj.get_calendar_list())
#
# calendar_list = obj.service.calendarList().list().execute()
# obj.add_calendar(
#     calendar_id='kladmoy04@mail.ru'
# )

# event = {
#   'summary': 'Тестовое название',
#   'location': 'Питер 52',
#   'description': 'Тестовое описание',
#   'start': {
#     'date': '2025-07-19'
#   },
#   'end': {
#     'date': '2025-07-20'
#   }
# }

# event1 = obj.add_event(calendar_id=calendar, body=event)
# pprint.pprint(obj.get_calendar_list())
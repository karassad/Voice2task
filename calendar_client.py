import pprint

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from tg_bot.config import TOKENS_DIR

SCOPES = ['https://www.googleapis.com/auth/calendar']
    # FILE_PATH = 'voice2task-462105-87ded2cfc0e1.json'
# TOKEN_DIR = "tg_bot/tokens"
class GoogleCalendar:

    def __init__(self, user_id: int):
        self.token_path = os.path.join(TOKENS_DIR, f"token_{user_id}.json")
        if not os.path.exists(self.token_path):
            raise FileNotFoundError(f"Пользователь {user_id} не авторизован")

        self.credentials = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # credentials = service_account.Credentials.from_service_account_file(
        #     filename=self.FILE_PATH, scopes = self.SCOPES
        # )
        self.service = build('calendar', 'v3', credentials=self.credentials)

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id: str, body: dict):
        return self.service.events().insert(calendarId=calendar_id, body=body).execute()
        # calendar_list_entry = {
        #     'id': calendar_id
        # }

        # return self.service.calendarList().insert(
        #     body=calendar_list_entry
        # ).execute()

    def add_event_to_primary(self, calendar_id, body):
        return self.service.events().insert(
            calendarId = 'primary',
            body=body
        ).execute()

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
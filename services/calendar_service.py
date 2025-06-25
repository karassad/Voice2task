import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class CalendarService:
    # Права доступа: создавать и редактировать события в календарях
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self, creds_path: str, token_path: str, timezone: str = 'Europe/Moscow'):
        self.creds_path = creds_path
        self.token_path = token_path
        self.timezone = timezone
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None

        if os.path.exists(
                'token.json'):  # В этом файле Google сохраняет токен авторизации, полученный после входа в аккаунт
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not creds or not creds.valid:  # токена нет или просрочен
            # создаёт OAuth-поток (через браузер)
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", self.SCOPES)
            creds = flow.run_local_server(port=8080)

            with open("token.json", "w") as token:
                token.write(creds.to_json())  # сохраняем токен в файл

        # Создаём объект service, через который можно делать запросы к Google Calendar API
        return build("calendar", "v3", credentials=creds)

    def list_calendars(self) -> list:
        '''
            Полyчение всех доступных календарей пользователя
        '''
        result = self.service.calendarList().list().execute()
        return result.get('items', [])

    def create_event(self, calendar_id: str, event: dict) -> str:
        '''
            Добавление события в выбранный календарь
            return ссылку на текущее событие
        '''
        google_event = {
            "summary": event["title"],
            "description": event.get("description", ""),
            "start": {
                "dateTime": event["start"],
                "timeZone": "Europe/Moscow",
            },
            "end": {
                "dateTime": event["end"],
                "timeZone": "Europe/Moscow",
            },
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": event.get("reminder_minutes", 10)}],
            },
        }

        print(f'Добавляем в календарь {calendar_id}:')
        print(json.dumps(google_event, indent=2, ensure_ascii=False))

        created_event = self.service.events().insert(calendarId=calendar_id, body=google_event).execute()
        return created_event.get('htmlLink')

from datetime import datetime
import os
import json

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Права доступа: создавать и редактировать события
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = None #авторизованные учётные данные
    if os.path.exists('token.json'):#В этом файле Google сохраняет токен авторизации, полученный после входа в аккаунт
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid: #токена нет или просрочен
        #создаёт OAuth-поток (через браузер)
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=8080)

        with open("token.json", "w") as token:
            token.write(creds.to_json()) #сохраняем токен в файл

    #Создаём объект service, через который можно делать запросы к Google Calendar API
    return build("calendar", "v3", credentials=creds)


def get_calendar_list():
    '''
        Полyчение всех доступных календарей пользователя
    '''
    service = get_calendar_service()
    result = service.calendarList().list().execute()
    return result.get('items', [])

def create_event_in_calendar(calendar_id: str, event: dict) -> str:
    '''
    Добавление события в выбранный календарь
    return ссылку на текущее событие
    '''
    service = get_calendar_service()

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

    created_event = service.events().insert(calendarId=calendar_id, body=google_event).execute()
    return created_event.get('htmlLink')


def create_event(event: dict) -> str:
    service = get_calendar_service()

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
    print("📦 Событие, отправляемое в Google Calendar:")
    print(json.dumps(event, indent=2, ensure_ascii=False))
    result = service.events().insert(calendarId="primary", body=google_event).execute()
    return result.get("htmlLink")
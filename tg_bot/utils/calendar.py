from datetime import datetime
import os
import json

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Права доступа: создавать и редактировать события
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


"""
    Получает сервис Google Calendar для конкретного пользователя.
    Использует токен из файла tokens/token_<user_id>.json
"""
def get_calendar_service(user_id: int):

    token_path = f'tokens/token_{user_id}.json'

    if not os.path.exists(token_path):
        raise FileNotFoundError("Пользователь не авторизован в Google")

    #загружаем credentials из JSON (выгружаем токен клиента)
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # creds = None #авторизованные учётные данные
    # if os.path.exists('token.json'):#В этом файле Google сохраняет токен авторизации, полученный после входа в аккаунт
    #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # if not creds or not creds.valid: #токена нет или просрочен
    #     #создаёт OAuth-поток (через браузер)
    #     flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    #     creds = flow.run_local_server(port=8080)
    #
    #     with open("token.json", "w") as token:
    #         token.write(creds.to_json()) #сохраняем токен в файл
    #
    # #Создаём объект service, через который можно делать запросы к Google Calendar API

    return build("calendar", "v3", credentials=creds)

"""
    Создаёт событие в календаре конкретного пользователя
    Принимает словарь event и user_id Telegram-пользователя
"""
def create_event(event: dict, user_id: int) -> str:
    service = get_calendar_service(user_id)

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

    result = service.events().insert(calendarId="primary", body=google_event).execute()
    return result.get("htmlLink")
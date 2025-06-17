import os

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
load_dotenv()

RAILWAY_REDIRECT = os.getenv("REDIRECT_URL", "https://web-production-25e89.up.railway.app/oauth2callback")
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def generate_google_auth_url(user_id: int) -> str:
    """
       Генерирует ссылку для авторизации Google Calendar через OAuth 2.0
       для конкретного Telegram-пользователя
       Аргументы:
           user_id (int): Telegram user ID, чтобы сохранить токен под ним\
       Возвращает:
           str: Ссылка на страницу авторизации Google (user -> browser)
    """

    flow = Flow.from_client_secrets_file(
        "credentials.json",  # файл, в котором лежат client_id, client_secret и redirect_uri
        scopes=SCOPES,
        redirect_uri = RAILWAY_REDIRECT
    )

    # генерим ссылку
    #дополнительные параметры, которые настраивают поведение авторизации Google OAuth 2.0
    auth_url, _ = flow.authorization_url(
        access_type="offline", #чтобы получить refresh_token (позволяет работать без повторной авторизации)
        include_granted_scopes="true", # не запрашивать заново уже одобренные права у клиента
        prompt="consent",  #заставляет Google показать экран авторизации (даже если уже вошёл) чтобы мы точно получили refresh token
        state=str(user_id)
    )

    return auth_url





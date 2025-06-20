import json
import os


from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
load_dotenv()

RAILWAY_REDIRECT = os.getenv("REDIRECT_URL")
if not RAILWAY_REDIRECT:
    raise ValueError("REDIRECT_URL не задан в переменных окружения!")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

GOOGLE_CREDS = os.getenv("GOOGLE_CREDENTIALS_JSON")
creds_dict = json.loads(GOOGLE_CREDS)

def generate_google_auth_url(user_id: int) -> str:
    """
       Генерирует ссылку для авторизации Google Calendar через OAuth 2.0
       для конкретного Telegram-пользователя
       Аргументы:
           user_id (int): Telegram user ID, чтобы сохранить токен под ним\
       Возвращает:
           str: Ссылка на страницу авторизации Google (user -> browser)
    """
    try:
        print(f"REDIRECT_URL = {RAILWAY_REDIRECT}")

        flow = Flow.from_client_secrets_file(
            creds_dict['web'],  # файл, в котором лежат client_id, client_secret и redirect_uri
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
    except Exception as e:
        import traceback
        print("❌ Ошибка при генерации ссылки авторизации:")
        traceback.print_exc()
        raise e





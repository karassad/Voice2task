from dotenv import load_dotenv
from fastapi import FastAPI, Request #FastAPI фреймворк для создания HTTP API-серверов
from google_auth_oauthlib.flow import Flow #объект от Google, который помогает провести OAuth 2.0 авторизацию.
import os
load_dotenv()

from tg_bot.config import TOKENS_DIR

app = FastAPI() #приложение апи
print("✅ FastAPI app instance создан")

SCOPES = ["https://www.googleapis.com/auth/calendar.events"] #разрешение на добавленрие в календарь
CLIENT_SECRET_FILE = "auth/credentials.json" #OAuth 2.0

#обработка GET-запросов
@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    print("FastAPI успешно запущен")
    try:
        user_id = request.query_params.get("state") #пользователь
        code = request.query_params.get('code') #код для получения токена

        print("CALLBACK ПОЛУЧЕН")
        print(f"user_id = {user_id}")
        print(f"code = {code}")

        flow = Flow.from_client_secrets_file( #читает credentials.json
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri=os.getenv("REDIRECT_URL") #куда Google вернёт пользователя после входа
        )

        #содержит всё, что нужно для работы с Google API от имени конкретного пользователя.
        flow.fetch_token(code=code) # Обмениваем code на access_token и refresh_token
        creds = flow.credentials #объект с авторизацией

        os.makedirs(TOKENS_DIR, exist_ok=True)
        token_path = os.path.join(TOKENS_DIR, f"token_{user_id}.json")
        print("👉 TOKENS_DIR =", TOKENS_DIR)
        print("👉 DIR EXISTS:", os.path.exists(TOKENS_DIR))

        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

        print(f"Токен сохранён: {token_path}")

        return {"message": "Авторизация успешна. Можно вернуться в Telegram-бот."}
    except Exception as e:
        print("❌ Ошибка в oauth2callback:")
        import traceback
        traceback.print_exc()
        return {"error": "Internal error"}






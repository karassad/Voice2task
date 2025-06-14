from fastapi import FastAPI, Request #FastAPI фреймворк для создания HTTP API-серверов
from google_auth_oauthlib.flow import Flow #объект от Google, который помогает провести OAuth 2.0 авторизацию.
import os

app = FastAPI() #приложение апи

SCOPES = ["https://www.googleapis.com/auth/calendar.events"] #разрешение на добавленрие в календарь
CLIENT_SECRET_FILE = "credentials.json" #OAuth 2.0

#обработка GET-запросов
@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    user_id = request.query_params.get("state") #пользователь
    code = request.query_params.get('code') #код для получения токена

    flow = Flow.from_client_secrets_file( #читает credentials.json
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=os.getenv("REDIRECT_URL") #куда Google вернёт пользователя после входа
    )

    #содержит всё, что нужно для работы с Google API от имени конкретного пользователя.
    flow.fetch_token(code=code) # Обмениваем code на access_token и refresh_token
    creds = flow.credentials #объект с авторизацией

    os.makedirs('../Voice2task/tokens', exist_ok=True)
    with open(f'../Voice2task/tokens/token_{user_id}.json', 'w') as token_file:
        token_file.write(creds.to_json())
    return {"message": "Авторизация успешна. Можно вернуться в Telegram-бот."}







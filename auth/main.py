import json
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request  # FastAPI фреймворк для создания HTTP API-серверов
from google_auth_oauthlib.flow import Flow  # объект от Google, который помогает провести OAuth 2.0 авторизацию.

from tg_bot.config import TOKENS_DIR

load_dotenv()

# настройка логирования
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()  # приложение апи
logger.info("✅ FastAPI app instance создан")

SCOPES = ["https://www.googleapis.com/auth/calendar"]  # разрешение на добавленрие в календарь
# CLIENT_SECRET_FILE = "auth/credentials.json" #OAuth 2.0
GOOGLE_CREDS = os.getenv("GOOGLE_CREDENTIALS_JSON")
creds_dict = json.loads(GOOGLE_CREDS)

# обработка GET-запросов
@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    logger.info("FastAPI успешно запущен")
    try:
        user_id = request.query_params.get("state")  # пользователь
        code = request.query_params.get('code')  # код для получения токена

        logger.info("CALLBACK ПОЛУЧЕН")
        logger.info(f"user_id = {user_id}")
        logger.info(f"code = {code}")

        if not user_id or not code:
            logger.error("Не получены параметры 'state' или 'code'")
            return {"error": "missing parameters"}

        logger.info(f"👉 REDIRECT_URL = {os.getenv('REDIRECT_URL')}")
        logger.info(f"👉 SCOPES = {SCOPES}")

        flow = Flow.from_client_config(  # читает credentials.json
            creds_dict,
            scopes=SCOPES,
            redirect_uri=os.getenv("REDIRECT_URL")  # куда Google вернёт пользователя после входа
        )

        # содержит всё, что нужно для работы с Google API от имени конкретного пользователя.
        flow.fetch_token(code=code)  # Обмениваем code на access_token и refresh_token
        creds = flow.credentials  # объект с авторизацией

        os.makedirs(TOKENS_DIR, exist_ok=True)
        token_path = os.path.join(TOKENS_DIR, f"token_{user_id}.json")
        logger.info(f"👉 TOKENS_DIR = {TOKENS_DIR}")
        logger.info(f"👉 DIR EXISTS: {os.path.exists(TOKENS_DIR)}")

        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

        logger.info(f"Токен сохранён: {token_path}")

        return {"message": "Авторизация успешна. Можно вернуться в Telegram-бот."}
    except Exception as e:
        logger.error("❌ Ошибка в oauth2callback:")
        logger.exception(e)
        return {"error": "Internal error"}

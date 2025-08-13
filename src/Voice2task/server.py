import json
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates
from telegram import Update
from telegram.ext import Application
from .db_services.user_storage import UserStorage
from .handlers.oauth_handler import OauthHandler


templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
templates = Jinja2Templates(directory=templates_dir)


bot_app: Application | None = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """
        Функция, которая будет выполняться при запуске и остановке сервера FastAPI.
        Используется для асинхронной инициализации и очистки ресурсов.
    """
    global bot_app
    bot_app = fastapi_app.telegram_app_instance
    await bot_app.initialize() #инициализация application

    if bot_app and fastapi_app.webhook_url:
        try:
            await bot_app.bot.set_webhook(fastapi_app.webhook_url)
            logger.info(f"Webhook set to {fastapi_app.webhook_url}")
        except Exception as e:
            logger.error(f"Error setting webhook: {e}", exc_info=True)

    yield

    try:
        await bot_app.bot.delete_webhook()
        logger.info("Webhook deleted successfully.")
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}", exc_info=True)

fastapi_app = FastAPI(lifespan=lifespan)

@fastapi_app.post('/webhook_dev')
async def webhook(request: Request):
    try:
        update_data = await request.json()
        logger.info(f"Received webhook data: {update_data}")

        update = Update.de_json(update_data, bot_app.bot)
        await bot_app.process_update(update)

        return {'ok': True}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return {'ok': False, 'error': str(e)}

@fastapi_app.get('/oauth_callback')
async def oauth_callback(request: Request):
    oauth_handler = OauthHandler()
    user_storage = UserStorage()

    try:
        state = int(request.query_params.get('state'))
        credentials = await oauth_handler.get_user_credentials(request)
        logger.info(f"OAuth callback received for state: {state}. credentials: {credentials}")

        try:
            if credentials and state:
                old_credentials_json = await user_storage.get_user_token(state)
                old_refresh_token = None

                if old_credentials_json:
                    old_credentials_dict = json.loads(old_credentials_json)
                    old_refresh_token = old_credentials_dict.get('refresh_token')
                    logger.info(f"Found old refresh_token: {old_refresh_token}")

                final_refresh_token = credentials.refresh_token if credentials.refresh_token else old_refresh_token

                credentials_dict = {
                    'token': credentials.token,
                    'refresh_token': final_refresh_token,
                    'token_uri': credentials.token_uri,
                    'client_id': credentials.client_id,
                    'client_secret': credentials.client_secret,
                    'scopes': credentials.scopes
                }

                logger.info(f"Saving credentials for user {state}: {credentials_dict} in callback_oauth")

                await user_storage.set_user_data(state, credentials_dict)
                logger.info(f"Credentials saved successfully for user {state}.")

                return templates.TemplateResponse('auth_success.html', {"request": request})
            else:
                logger.error(f"Invalid credentials or state for user {state}.")

        except Exception as e:
            logger.error(f"Error saving credentials for user {state}: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}", exc_info=True)



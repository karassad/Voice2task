import logging
import secrets
from telegram.ext import ContextTypes

from src.Voice2task.tg_services.message_utils.message_send_logic import send_smart_message
from google_auth_oauthlib.flow import Flow
from telegram import Update
from fastapi import Request
from src.Voice2task.db_services.user_storage import UserStorage
from src.Voice2task.config import GOOGLE_CLIENT_SECRET, SCOPES, REDIRECT_URI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
oauth_sessions: dict[str, Flow] = {}

class OauthHandler:
    def __init__(self):
        self.client_secret = GOOGLE_CLIENT_SECRET
        self.scopes = SCOPES
        self.redirect_uri = REDIRECT_URI
        self.user_storage = UserStorage()

    async def create_auth_url(self, user_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Создает URL для авторизации пользователя в Google OAuth 2.0.
        :param user_id
        :param update:
        :return: authorization URL
        """
        state = secrets.token_urlsafe(32) #state для защиты от CSRF атак, уникальный для каждого запроса
        await self.user_storage.update_user_data(user_id, {
            'state': state})


        flow = Flow.from_client_secrets_file(
            client_secrets_file=self.client_secret,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )

        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline', #режим оффлайн для получения refresh токена
            include_granted_scopes='true', #список разрешений
            state=state
        )

        oauth_sessions[state] = flow
        logger.info(f"Saved OAuth flow for state: {state}")

        await send_smart_message(update=update, context=context, text='Пожалуйста, перейдите по следующей ссылке для авторизации: ' + auth_url, last_message=False, reply_markup=None)

    async def get_user_credentials(self, request: Request):
        '''
        Обрабатывает запрос на получение токенов доступа после авторизации пользователя.
        :param request:
        :return: credentials
        '''
        logger.info("Received Google OAuth2 callback request.")
        state = request.query_params.get('state')
        code = request.query_params.get('code')

        flow = oauth_sessions.get(state)
        if not flow:
            logger.error(f"OAuth flow not found for state: {state}")
            return None

        try:
            flow.fetch_token(code=code)
            credentials = flow.credentials
            logger.info(f"Fetched credentials for state {state}: {credentials.token}")
            del oauth_sessions[state]
            return credentials
        except Exception as e:
            logger.error(f"Error fetching token for state {state}: {e}", exc_info=True)
            return None

    async def user_auth_process(self, user_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает процесс авторизации пользователя.
        :param state: user_id
        :param update: Update object
        """
        # us = UserStorage()
        # from ..google_calendar_services.main_calendar_setup import MainCalendarSetup
        try:
            logger.info(f"User {user_id} is not authorized. Creating auth URL.")
            await self.create_auth_url(int(user_id), update, context)

        except Exception as e:
            logger.error(f"Error during user authorization process for user {user_id}: {e}", exc_info=True)

    async def verify_state_and_get_user_id(self, state: str):
        """
        Проверяет, соответствует ли полученный state сохраненному,
        и возвращает user_id.
        """
        docs = self.user_storage.db.collection('users_dev').stream()
        for doc in docs:
            data = doc.to_dict()
            try:
                decrypted_state = self.user_storage._decrypt_value(data.get('state'))
                if decrypted_state == state:
                    await self.user_storage.update_user_data(int(doc.id), {'state': None})
                    return int(doc.id)

            except Exception as e:
                logger.error(f"Error verify state for user {doc.id}: {e}", exc_info=True)
        return None

    # async def oauth_success(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     """
    #         Вызывается после успешного завершения авторизации.
    #         Запускает процесс выбора основного календаря.
    #     """
    #     user_id = update.effective_user.id
    #     logger.info(f"OAuth success for user {user_id}. Starting main calendar setup.")
    #     main_calendar_setup = MainCalendarSetup()
    #     try:
    #         await main_calendar_setup.start_calendar_selection_flow(update, context)
    #     except Exception as e:
    #         logger.error(f"Error starting main calendar setup for user {user_id}: {e}", exc_info=True)
    #






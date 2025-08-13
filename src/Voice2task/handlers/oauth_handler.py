import logging

from google_auth_oauthlib.flow import Flow
from telegram import Update
from fastapi import Request
from ..db_services.user_storage import UserStorage
from ..config import GOOGLE_CLIENT_SECRET, SCOPES, REDIRECT_URI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
oauth_sessions: dict[str, Flow] = {}

class OauthHandler:
    def __init__(self):
        self.client_secret = GOOGLE_CLIENT_SECRET
        self.scopes = SCOPES
        self.redirect_uri = REDIRECT_URI

    async def create_auth_url(self, state: str, update: Update):
        """
        Создает URL для авторизации пользователя в Google OAuth 2.0.
        :param state:
        :param update:
        :return: authorization URL
        """
        flow = Flow.from_client_secrets_file(
            client_secrets_file=self.client_secret,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )

        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline', #режим оффлайн для получения refresh токена
            include_granted_scopes='true', #список разрешений
            state=state, #user_id
        )

        oauth_sessions[state] = flow
        logger.info(f"Saved OAuth flow for state: {state}")

        await update.message.reply_text('Пожалуйста, перейдите по следующей ссылке для авторизации: ' + auth_url)

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

    async def user_auth_process(self, state: str, update: Update):
        """
        Обрабатывает процесс авторизации пользователя.
        :param state: user_id
        :param update: Update object
        """
        us = UserStorage()
        try:
            if await us.get_user_token(int(state)) != False:
                logger.info(f"User {state} is already authorized.")
                #логика запуска флоу
            else:
                logger.info(f"User {state} is not authorized. Creating auth URL.")
                await self.create_auth_url(state, update)

        except Exception as e:
            logger.error(f"Error during user authorization process for user {state}: {e}", exc_info=True)






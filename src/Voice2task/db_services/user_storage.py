import asyncio
import logging
import os

from google.oauth2 import service_account

from ..config import GOOGLE_CLIENT_SECRET, FIREBASE_PROJECT_ID, FIREBASE_SERVICE_ACCOUNT_KEY_PATH
import firebase_admin
from firebase_admin import firestore, credentials
# from google.cloud import firestore


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

is_firebase_admin = False

class UserStorage:
    """
        Класс для хранения пользовательских данных (токенов, выбранного календаря)
        с использованием бд Firestore.
    """
    def __init__(self):
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            cred_path = os.path.join(base_dir, FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
            creds = service_account.Credentials.from_service_account_file(
                cred_path
            )
            global is_firebase_admin
            if not is_firebase_admin:
                self.app = firebase_admin.initialize_app(creds, options={
                    'projectId': creds.project_id})  # инициализируем общее соединение с Firebase
                is_firebase_admin = True
            self.db = firestore.client() #создаем конкретного клиента для работы с Firestore
        except Exception as e:
            logger.error(f"Ошибка при инициализации Firestore: {e}", exc_info=True)
            raise

    async def set_user_data(self, user_id: int, data: dict):
        """
        Сохраняет данные пользователя в Firestore, полностью переписывет все поля
        :param user_id: ID пользователя Telegram.
        :param data: Словарь с данными пользователя, которые нужно сохранить.
        """
        try:
            doc_ref = self.db.collection('users_dev').document(str(user_id))
            await asyncio.to_thread(doc_ref.set, data)
            logger.info(f"User data for {user_id} saved successfully.")
        except Exception as e:
            logger.error(f"Error saving user data for {user_id}: {e}", exc_info=True)
            raise

    async def update_user_data(self, user_id: int, data: dict):
        """
        Обновляет данные пользователя в Firestore или добавляет ногвое поле.
        :param user_id: ID пользователя Telegram.
        :param data: Словарь с данными пользователя, которые нужно обновить.
        """
        try:
            doc_ref = self.db.collection('users_dev').document(str(user_id))
            await asyncio.to_thread(doc_ref.update, data)
            logger.info(f"User data for {user_id} saved successfully.")
        except Exception as e:
            logger.error(f"Error saving user data for {user_id}: {e}", exc_info=True)
            raise

    async def get_main_calendar(self, user_id: int):
        """
        Получает основной календарь пользователя из Firestore.
        :param user_id: ID пользователя Telegram.
        """
        try:
            doc_ref = self.db.collection('users_dev').document(str(user_id))
            fields = await asyncio.to_thread(doc_ref.get)
            if fields.exists:
                data = fields.to_dict()
                if 'calendar' in data:
                    logger.info(f"Main calendar for {user_id} retrieved successfully.")
                    return data['calendar']
                else:
                    return False
            logger.info(f"Main calendar for {user_id} retrieved successfully.")
            return False
        except Exception as e:
            logger.error(f"Error saving user data for {user_id}: {e}", exc_info=True)
            raise

    async def get_user_token(self, user_id: int):
        """
        Получает токен авторизации пользователя из Firestore.
        :param user_id: ID пользователя Telegram.
        """
        try:
            doc_ref = self.db.collection('users_dev').document(str(user_id))
            fields = await asyncio.to_thread(doc_ref.get)
            if fields.exists:
                data = fields.to_dict()
                if 'token' in data:
                    logger.info(f"token for {user_id} retrieved successfully.")
                    return data['token']
                else:
                    return False
            logger.info(f"User token for {user_id} retrieved successfully.")
            return False
        except Exception as e:
            logger.error(f"Error saving user data for {user_id}: {e}", exc_info=True)
            raise

    async def get_user_data(self, user_id: int):
        """
        Получает данные пользователя из Firestore.
        :param user_id: ID пользователя Telegram.
        """
        try:
            doc_ref = self.db.collection('users_dev').document(str(user_id))
            fields = await asyncio.to_thread(doc_ref.get)
            if fields.exists:
                data = fields.to_dict()
                return data
            else:
                logger.info(f"User data for {user_id} not found.")
                return False
        except Exception as e:
            logger.error(f"Error getting user data for {user_id}: {e}", exc_info=True)
            raise


# us = UserStorage()
# us.set_user_data(123, {'k': 'lala', 'token': '12345'})
# # us.update_user_data(123, {'token': '123'})
# print(us.get_main_calendar(123))
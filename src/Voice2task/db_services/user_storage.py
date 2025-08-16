import asyncio
import logging
import os

from cryptography.fernet import Fernet
from google.oauth2 import service_account
from rsa.cli import encrypt

from ..config import FIREBASE_SERVICE_ACCOUNT_KEY_PATH, FERNET_KEY
import firebase_admin
from firebase_admin import firestore


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
            creds = service_account.Credentials.from_service_account_file(cred_path)

            global is_firebase_admin
            if not is_firebase_admin:
                self.app = firebase_admin.initialize_app(creds, options={
                    'projectId': creds.project_id})  # инициализируем общее соединение с Firebase
                is_firebase_admin = True

            self.db = firestore.client() #создаем конкретного клиента для работы с Firestore

            if not FERNET_KEY:
                logger.error("FERNET_KEY не установлен в переменных окружения")
                raise ValueError("FERNET_KEY не установлен.")

            self.fernet = Fernet(FERNET_KEY)
            logger.info("Fernet encryption initialized with provided key.")

        except Exception as e:
            logger.error(f"Ошибка при инициализации Firestore: {e}", exc_info=True)
            raise


    def _encrypt_value(self, value: str):
        """
        Шифрует значение с помощью Fernet.
        :param value: Значение для шифрования.
        :return: Зашифрованное значение.
        """
        if isinstance(value, str):
            try:
                encrypted_value = self.fernet.encrypt(value.encode('utf-8')) #закодированные байты
                return encrypted_value.decode('utf-8') #закодированная строка
            except Exception as e:
                logger.error(f"Error encrypting value: {e}", exc_info=True)


    def _decrypt_value(self, value: str):
        """
        Дешифрует значение с помощью Fernet.
        :param value: Зашифрованное значение.
        :return: Дешифрованное значение.
        """
        if isinstance(value, str):
            try:
                decrypted_value = self.fernet.decrypt(value.encode('utf-8'))
                return decrypted_value.decode('utf-8')
            except Exception as e:
                logger.error(f"Error decrypting value: {e}", exc_info=True)

    def _encrypt_dict_values(self, data: dict):
        """Шифрует только значения словаря."""
        encrypted_data = {}
        for key, value in data.items():
            if isinstance(value, list):
                # Если значение - это список, шифруем каждый элемент списка
                encrypted_data[key] = [self._encrypt_value(item) for item in value]
            else:
                encrypted_data[key] = self._encrypt_value(value)
        return encrypted_data

    def _decrypt_dict_values(self, data: dict):
        """Расшифровывает только значения словаря."""
        decrypted_data = {}
        for key, value in data.items():
            if isinstance(value, list):
                # Если значение - это список, расшифровываем каждый элемент списка
                decrypted_data[key] = [self._decrypt_value(item) for item in value]
            else:
                decrypted_data[key] = self._decrypt_value(value)
        return decrypted_data

    async def set_user_data(self, user_id: int, data: dict):
        """
        Сохраняет данные пользователя в Firestore, полностью переписывет все поля
        :param user_id: ID пользователя Telegram.
        :param data: Словарь с данными пользователя, которые нужно сохранить.
        """
        try:
            encrypted_data = self._encrypt_dict_values(data)
            doc_ref = self.db.collection('users_dev').document(str(user_id))
            await asyncio.to_thread(doc_ref.set, encrypted_data)
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
            encrypted_data = self._encrypt_dict_values(data)
            doc_ref = self.db.collection('users_dev').document(str(user_id))
            await asyncio.to_thread(doc_ref.set, encrypted_data, merge=True)
            logger.info(f"User data for {user_id} saved successfully.")
        except Exception as e:
            logger.error(f"Error saving user data for {user_id}: {e}", exc_info=True)
            raise

    async def get_main_calendar(self, user_id: int):
        """
        Получает основной календарь пользователя из Firestore. Возвращает словарь с ID и именем календаря,
        :param user_id: ID пользователя Telegram.
        """
        try:
            doc_ref = self.db.collection('users_dev').document(str(user_id))
            fields = await asyncio.to_thread(doc_ref.get)
            if fields.exists:
                data = fields.to_dict()
                decrypted_data = self._decrypt_dict_values(data)
                if 'main_calendar_id' in decrypted_data:
                    logger.info(f"Main calendar for {user_id} retrieved successfully.")
                    return {
                        'id': decrypted_data.get('main_calendar_id'),
                        'name': decrypted_data.get('main_calendar_name')
                    }
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
                decrypted_data = self._decrypt_dict_values(data)
                if 'token' in data:
                    logger.info(f"token for {user_id} retrieved successfully.")
                    return decrypted_data['token']
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
                decrypted_data = self._decrypt_dict_values(data)
                return decrypted_data
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
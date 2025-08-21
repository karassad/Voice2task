import logging
import os
import subprocess

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from src.Voice2task.ai_services.gemini_parser import GeminiParser
from src.Voice2task.transcriber_services.vosk_transcriber import VoskTranscriber

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskMessageHandler:

    def __init__(self):
        self.vosk_transcriber = VoskTranscriber()
        self.gemini_parser = GeminiParser()

    def _convert_ogg_to_wav(self, ogg_path: str, wav_path: str):
        """
            Конвертирует OGG-файл в WAV с параметрами для Vosk.
        """
        """
            Конвертирует OGG-файл в WAV с параметрами для Vosk.
        """
        # -i: входной файл
        # -ar 16000: частота дискретизации 16 кГц
        # -ac 1: один аудиоканал (моно)
        # -y: перезаписать выходной файл, если он существует
        command = [
            'ffmpeg',
            '-i', ogg_path,
            '-ar', '16000',
            '-ac', '1',
            '-y', wav_path
        ]

        #Запускаем команду в отдельном процессе
        subprocess.run(command, check=True)

    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
            Обрабатывает голосовое сообщение: скачивает, конвертирует,
            распознает с помощью Vosk и передает текст на парсинг в нейронку.
        """
        user_id = update.effective_user.id
        ogg_path = f'voice_{user_id}.ogg' #формат гс от тг
        wav_path = f'voice_{user_id}.wav' #формат гс для Vosk

        try:
            file_id = update.message.voice.file_id
            user_voice = await context.bot.get_file(file_id)
            await user_voice.download_to_drive(ogg_path) #сохраняем файл гс на диск

            #Конвертируем OGG в WAV, чтобы Vosk мог его обработать
            self._convert_ogg_to_wav(ogg_path, wav_path)

            #передаем текст в vosk
            recognized_text = self.vosk_transcriber.transcribe_voice(wav_path)
            logger.info(f'Распознано: {recognized_text}')

            #передаем в нейронку
            await self.gemini_parser.parse_user_request(update, context, text=recognized_text)

            return ConversationHandler.END

        except Exception as e:
            logger.error(f"Error handling voice message for user {user_id}: {e}", exc_info=True)
            return ConversationHandler.END

        finally:
            if os.path.exists(ogg_path):
                os.remove(ogg_path)
            if os.path.exists(wav_path):
                os.remove(wav_path)

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает текстовое сообщение и передает его напрямую в GeminiParser.
        """
        user_message = update.message.text
        try:
            # Вызываем парсер Gemini напрямую с текстом из сообщения
            await self.gemini_parser.parse_user_request(update, context, text=user_message)
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"Error handling text message: {e}", exc_info=True)
            return ConversationHandler.END



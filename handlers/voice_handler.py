import json
from telegram import Update, Voice
from telegram.ext import ContextTypes

from flow.event_flow import EventCreationFlow
from services.transcriber import Transcriber
from services.gpt_parser import TaskParser
from utils.audio import convert_ogg_to_wav


"""
Обработчик голосовых сообщений Telegram-бота.
Получает voice.ogg, конвертирует в .wav, передаёт в Whisper и возвращает распознанный текст.
"""
class VoiceHandler:

    def __init__(self, transcriber: Transcriber, parser: TaskParser, flow: EventCreationFlow):
        self.transcriber = transcriber
        self.parser = parser
        self.flow = flow

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
            Обрабатывает голосовое сообщение пользователя:
            1. Скачивает .ogg
            2. Конвертирует в .wav
            3. Распознаёт текст
            4. Извлекает задачу
            5. Передаёт её в EventCreationFlow
        """

        voice: Voice = update.message.voice
        file = await context.bot.get_file(voice.file_id) #Получаем ссылку на скачивание голосового файла
        await  file.download_to_drive('voice.ogg') #Скачиваем голосовое сообщение

        convert_ogg_to_wav("voice.ogg", "voice.wav")
        text = self.transcriber.transcribe("voice.wav")

        await  update.message.reply_text(f"Распознанный текст:\n{text}")

        try:
            event = self.parser.parse(text) #получчаем питон словарь
            formatted = json.dumps(event, indent=2, ensure_ascii=False) #преобразует его в отформатированную JSON-строку

            await update.message.reply_text(
                f"📅 Задача из текста:\n<pre>{formatted}</pre>",
                parse_mode="HTML"
            )

            # Показываем инлайн-кнопки с календарями
            await self.flow.start(update, context, event)

        except Exception as e:
            import traceback
            traceback.print_exc()  # покажет ошибку в консоли
            await update.message.reply_text("Ошибка при создании события.")
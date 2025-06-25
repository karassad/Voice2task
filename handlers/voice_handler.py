import json

from telegram import Update, Voice
from telegram.ext import ContextTypes

from utils.flow import EventCreationFlow
from utils.transcriber import transcribe_audio
from utils.audio import convert_ogg_to_wav
from utils.gpt_parser import parse_task_to_event


"""
Обработчик голосовых сообщений Telegram-бота.
Получает voice.ogg, конвертирует в .wav, передаёт в Whisper и возвращает распознанный текст.
"""
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
        Обрабатывает голосовое сообщение пользователя
        1. Скачивает файл .ogg
        2. Конвертирует в .wav через ffmpeg
        3. Распознаёт речь через Whisper
        4. Отправляет текст пользователю
    """

    voice: Voice = update.message.voice
    file = await context.bot.get_file(voice.file_id) #Получаем ссылку на скачивание голосового файла
    await  file.download_to_drive('voice.ogg') #Скачиваем голосовое сообщение

    convert_ogg_to_wav("voice.ogg", "voice.wav")
    text = transcribe_audio("voice.wav")

    await  update.message.reply_text(f"Распознанный текст:\n{text}")

    try:
        event = parse_task_to_event(text) #получчаем питон словарь
        formatted = json.dumps(event, indent=2, ensure_ascii=False) #преобразует его в отформатированную JSON-строку
        print("📦 Событие, отправляемое в Google Calendar:")
        print(json.dumps(event, indent=2, ensure_ascii=False))
        #Добавляем в Google Calendar
        print("📦 Event object:", event)

        await update.message.reply_text(
            f"📅 Задача из текста:\n<pre>{formatted}</pre>",
            parse_mode="HTML"
        )

        # Показываем инлайн-кнопки с календарями
        await EventCreationFlow.start(update, context, event)



    except Exception as e:
        import traceback
        traceback.print_exc()  # покажет ошибку в консоли
        await update.message.reply_text("Ошибка при создании события.")
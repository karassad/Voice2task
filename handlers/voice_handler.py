from telegram import Update, Voice
from telegram.ext import ContextTypes
from utils.transcriber import transcribe_audio
from utils.audio import convert_ogg_to_wav


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
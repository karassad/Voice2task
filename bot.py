from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from whisper import transcribe

from config import BOT_TOKEN, GOOGLE_CREDS_PATH, GOOGLE_TOKEN_PATH, TIMEZONE

from services.calendar_service import CalendarService
from services.transcriber import Transcriber
from services.gpt_parser import TaskParser
from flow.event_flow import EventCreationFlow
from handlers.start_handler import start, handle_button
from handlers.voice_handler import VoiceHandler

"""
Главная точка входа для Telegram-бота.
Инициализирует бота, подключает обработчики команд, сообщений и кнопок.
"""

def build_bot():
    #Инициализация сервисов

    #сервис для работы с Google Calendar API
    calendar_service = CalendarService(GOOGLE_CREDS_PATH, GOOGLE_TOKEN_PATH, TIMEZONE)
    #Модель faster-whisper, для распознавания речи
    transcriber = Transcriber()
    #Обёртка над LLM (Ollama), преобразует текст в JSON-событие
    parser = TaskParser()
    #Флоу сценария с выбором календаря. Работает поверх calendar_service
    event_flow = EventCreationFlow(calendar_service)
    #Главный обработчик голосовых сообщений — объединяет все предыдущие.
    voice_handler = VoiceHandler(transcriber, parser, event_flow)

    # Инициализация Telegram-приложения
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler.handle_voice))
    app.add_handler(CallbackQueryHandler(handle_button, pattern=r"^(?!calendar_).*"))  # не-календарные кнопки
    app.add_handler(CallbackQueryHandler(event_flow.handle_calendar_selection, pattern=r"^calendar_"))  # календарные

    return app

if __name__ == "__main__":
    app = build_bot()
    print("🚀 Бот запущен...")
    app.run_polling()
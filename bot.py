import os

import uvicorn
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from server import app as fastapi_app  # FastAPI-приложение

from config import BOT_TOKEN, GOOGLE_CREDS_PATH, GOOGLE_TOKEN_PATH, TIMEZONE

from services.calendar_service import CalendarService
from services.transcriber import Transcriber
from services.gpt_parser import TaskParser
from flow.event_flow import EventCreationFlow
from handlers.start_handler import start, handle_button
from handlers.voice_handler import VoiceHandler
import asyncio

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
    # app = ApplicationBuilder().token(BOT_TOKEN).build()
    from telegram.request import HTTPXRequest
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(HTTPXRequest(connect_timeout=30, read_timeout=30))
        .build()
    )

    # Сохраняем event_flow для использования в хендлерах кнопок
    app.bot_data["event_flow"] = event_flow

    # Хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler.handle_voice))
    app.add_handler(CallbackQueryHandler(handle_button, pattern=r"^(?!calendar_).*"))  # не-календарные кнопки
    app.add_handler(CallbackQueryHandler(event_flow.handle_calendar_selection, pattern=r"^calendar_"))  # календарные

    return app


async def main():
    bot_app = build_bot()
    print("🚀 Бот запущен...")

    port = int(os.getenv("PORT", 8000))
    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)

    await asyncio.gather(
        bot_app.initialize(),
        bot_app.run_polling(),
        server.serve()
    )


if __name__ == "__main__":
    asyncio.run(main())


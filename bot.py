from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

from config import BOT_TOKEN
from handlers.voice_handler import handle_voice
from handlers.start_handler import start, handle_button
from telegram.ext import CallbackQueryHandler
from utils.flow import EventCreationFlow


"""
Главная точка входа для Telegram-бота.
Инициализирует бота, подключает обработчики команд, сообщений и кнопок.
"""

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
# app.add_handler(CallbackQueryHandler(handle_button)) #обработка нажатия на inline-кнопки
# app.add_handler(CallbackQueryHandler(EventCreationFlow.handle_calendar_selection))
# Первый обрабатывает кнопки с callback_data, начинающейся на "start_" или другие команды
app.add_handler(CallbackQueryHandler(handle_button, pattern=r"^(?!calendar_).*"))
# Второй — только для календарей
app.add_handler(CallbackQueryHandler(EventCreationFlow.handle_calendar_selection, pattern=r"^calendar_"))

print("Бот запущен...")
app.run_polling() #Это основной цикл работы бота
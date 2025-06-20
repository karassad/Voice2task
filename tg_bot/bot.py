from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from telegram import Update

from config import BOT_TOKEN
from handlers.start_handler import start, handle_button

from telegram.ext import CallbackQueryHandler

print("Бот запущен...")



"""
Главная точка входа для Telegram-бота.
Инициализирует бота, подключает обработчики команд, сообщений и кнопок.
"""

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(CallbackQueryHandler(handle_button)) #обработка нажатия на inline-кнопки




if __name__ == "__main__":
    print("▶️ Бот запускается (polling)")
    app.run_polling()
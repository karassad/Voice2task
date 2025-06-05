from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

"""
Обработчики команд и кнопок при запуске бота.

- Команда /start отправляет приветствие и кнопку "Начать".
- Нажатие кнопки вызывает инструкцию для пользователя.
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Начать", callback_data="start_voice_input")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет! Я помогу тебе создавать задачи по голосу.",
        reply_markup=reply_markup
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query #callback_query - спец событие inline-кнопки
    await query.answer() #показываем тг, что мы приняли запрос

    if query.data == "start_voice_input":
        await query.edit_message_text("Отправь мне голосовое сообщение, и я создам задачу!")

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.user_storage import UserStorage

"""
Обработчики команд и кнопок при запуске бота.

- Команда /start отправляет приветствие и кнопку "Начать".
- Нажатие кнопки вызывает инструкцию для пользователя.
"""

storage = UserStorage()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    calendar_id = storage.get_calendar(user_id)

    buttons = [
        [InlineKeyboardButton("📝 Создать задачу", callback_data="create_task")],
        [InlineKeyboardButton("📅 Сменить основной календарь", callback_data="change_calendar")]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    welcome_text = (
        "<b>Привет!</b>\n\n"
        f"Текущий основной календарь: <code>{calendar_id if calendar_id else 'не выбран'}</code>\n\n"
        "Выбери, что хочешь сделать:"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query #callback_query - спец событие inline-кнопки
    user_id = update.effective_user.id
    await query.answer() #показываем тг, что мы приняли запрос


    if query.data == "create_task":
        calendar_id = storage.get_calendar(user_id)
        if not calendar_id:
            event_flow = context.application.bot_data.get('event_flow')
            if not event_flow:
                await query.edit_message_text("Внутренняя ошибка: сценарий не инициализирован.")
                return
            await query.edit_message_text("У вас не выбран календарь. Секунду, загружаю список календарей...")
            await event_flow.start(update, context, event=None)
        else:
            await query.edit_message_text("Отправьте голосовое сообщение для создания задачи.")

    elif query.data == 'change_calendar':
        event_flow = context.application.bot_data.get('event_flow')
        if not event_flow:
            await query.edit_message_text("Внутренняя ошибка: сценарий не инициализирован.")
            return
        await query.edit_message_text("Секунду, загружаю список календарей...")
        await event_flow.start(update, context, event=None)


async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("📝 Создать задачу", callback_data="create_task")],
        [InlineKeyboardButton("📅 Сменить календарь", callback_data="change_calendar")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Что хотите сделать дальше?",
        reply_markup=reply_markup
    )


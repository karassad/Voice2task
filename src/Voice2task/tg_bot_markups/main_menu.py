from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot, Update
from ..db_services.user_storage import UserStorage


async def send_main_menu(bot: Bot, chat_id: int, update: Update):

    user_storage = UserStorage()
    calendar_name = await user_storage.get_main_calendar(int(update.effective_user.id))

    buttons = [
        [InlineKeyboardButton("📝 Создать задачу", callback_data="create_task")],
        [InlineKeyboardButton("📞 Создать созвон (Google Meet)", callback_data="create_meet")],
        [InlineKeyboardButton("📅 Сменить календарь", callback_data="change_calendar")],
        [InlineKeyboardButton("🔄 Рестарт бота (повторная авторизация)", callback_data="restart")],
    ]
    markup = InlineKeyboardMarkup(buttons)

    calendar_text = (
        f"<b>{calendar_name}</b>" if calendar_name else "<b>не выбран</b>"
    )

    await bot.send_message(
        chat_id=chat_id,
        text=f"Сейчас Ваш текущий основной календарь: {calendar_text}.",
        parse_mode="HTML",
        reply_markup=markup
    )
